/**
 * Sanitize headers by removing sensitive information.
 */
export function sanitizeHeaders(headers) {
  if (!headers) return {};
  
  const sanitized = { ...headers };
  const sensitiveKeys = ['authorization', 'cookie', 'set-cookie', 'apikey', 'x-api-key'];
  
  // Axios headers might be AxiosHeaders objects or plain objects.
  // We normalize to lowercase keys for checking.
  for (const key in sanitized) {
    if (sensitiveKeys.includes(key.toLowerCase())) {
      sanitized[key] = '[REDACTED]';
    }
  }
  
  return sanitized;
}

/**
 * Safely stringify an object and truncate it if it exceeds maxLen.
 */
export function shortJson(obj, maxLen = 2000) {
  try {
    const str = JSON.stringify(obj);
    if (str.length > maxLen) {
      return str.substring(0, maxLen) + '... [TRUNCATED]';
    }
    return str;
  } catch (e) {
    return '[Unserializable Object]';
  }
}
