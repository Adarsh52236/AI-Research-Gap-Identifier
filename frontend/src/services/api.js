import axios from 'axios';
import { DEBUG } from '../config/debug';
import { sanitizeHeaders, shortJson } from '../utils/sanitize';
import useAppStore from '../store/useAppStore';

const base = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");
const api = axios.create({
  baseURL: `${base}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = useAppStore.getState().auth.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Generate client request ID
  const cid = crypto.randomUUID();
  config.headers['X-Client-Request-Id'] = cid;
  config.metadata = { startTime: Date.now(), cid };

  if (DEBUG) {
    const fullUrl = `${config.baseURL || ''}${config.url}`;
    console.groupCollapsed(`[API REQUEST] ${(config.method || 'GET').toUpperCase()} ${fullUrl}`);
    console.log('cid:', cid);
    console.log('url:', fullUrl);
    if (config.params) console.log('params:', config.params);
    console.log('headers:', sanitizeHeaders(config.headers));
    if (config.data) {
      console.log('payload summary:', shortJson(config.data));
    }
    console.groupEnd();
  }

  return config;
});

api.interceptors.response.use(
  (response) => {
    const { startTime, cid } = response.config.metadata || {};
    const elapsed = startTime ? Date.now() - startTime : null;
    
    // Extract backend request id if present
    const backendReqId = response.headers['x-request-id'] || response.data?.error?.request_id;
    
    if (DEBUG) {
      console.groupCollapsed(`[API RESPONSE] ${response.status} (${elapsed}ms)`);
      console.log('cid:', cid);
      console.log('status:', response.status);
      console.log('elapsed:', elapsed, 'ms');
      
      const safeHeaders = {
        'content-type': response.headers['content-type'],
        'x-request-id': response.headers['x-request-id'],
        'x-render-origin-server': response.headers['x-render-origin-server'],
        'cf-ray': response.headers['cf-ray'],
        'rndr-id': response.headers['rndr-id'],
        'x-service': response.headers['x-service'],
        'x-env': response.headers['x-env']
      };
      console.log('headers:', safeHeaders);
      if (backendReqId) {
         console.log('backend request_id:', backendReqId);
      }
      console.groupEnd();
    }
    
    // Update debug state
    useAppStore.getState().setDebugState({
       lastRequest: {
         method: response.config.method?.toUpperCase(),
         url: response.config.url,
         status: response.status,
         request_id: backendReqId || cid
       }
    });

    return response;
  },
  (error) => {
    let classification = '[API ERROR][UNKNOWN]';
    let backendReqId = null;

    if (error.response) {
      const status = error.response.status;
      backendReqId = error.response.headers?.['x-request-id'] || error.response.data?.error?.request_id;
      
      if (status === 401) {
        classification = '[API ERROR][HTTP_401] Unauthorized';
        useAppStore.getState().logout();
        document.dispatchEvent(new CustomEvent('open-auth'));
      } else if (status === 404) {
        classification = '[API ERROR][HTTP_404] Not Found';
      } else if (status === 429) {
        classification = '[API ERROR][HTTP_429] Rate Limited';
      } else if ([502, 503, 504].includes(status)) {
        classification = `[API ERROR][HTTP_${status}] Gateway/Timeout`;
      } else if (status >= 500) {
        classification = `[API ERROR][HTTP_${status}] Server Error`;
      } else {
         classification = `[API ERROR][HTTP_${status}]`;
      }
    } else if (error.request) {
      classification = '[API ERROR][NETWORK_CORS_TIMEOUT] No response received';
    } else {
      classification = '[API ERROR][SETUP] Request setup error';
    }

    if (DEBUG) {
      console.log(classification, error.message);
      if (error.response) {
        console.log('status:', error.response.status);
        console.log('data:', shortJson(error.response.data));
        console.log('headers:', sanitizeHeaders(error.response.headers));
        
        if ([502, 503, 504].includes(error.response.status)) {
           console.log("Likely backend sleeping/timeout on Render free tier. Try again or slow polling.");
        }
        if (error.response.status === 404 && error.config.url.includes('pipeline-run')) {
           console.log("Run ID not found; possible stateless run store misconfiguration.");
        }
        if (backendReqId) {
           console.log(`Backend request_id=${backendReqId} (use Render logs search).`);
        }
      }
    }
    
    // Update debug state
    useAppStore.getState().setDebugState({
       lastError: classification + (backendReqId ? ` (req_id: ${backendReqId})` : '')
    });

    return Promise.reject(error);
  }
);

export default api;
