import { Link } from 'react-router-dom';
import useAppStore from '../store/useAppStore';

export default function Dashboard() {
  const { report } = useAppStore();

  if (!report) {
    return (
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-white shadow rounded text-center">
        <h2 className="text-xl mb-4">No report available.</h2>
        <Link to="/analysis" className="text-blue-600 hover:underline">Go back to Analysis</Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="mb-6 flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Gap Report</h1>
          <p className="text-gray-500">Query: {report.query}</p>
        </div>
        <Link to="/" className="text-blue-600 hover:underline font-medium">Start New Search</Link>
      </div>

      <div className="space-y-8">
        {report.gaps && report.gaps.map((gap, i) => (
          <div key={gap.gap_id || i} className="bg-white p-6 rounded border border-gray-200 shadow-sm">
            <div className="flex items-start justify-between">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">{gap.title}</h2>
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-medium">Confidence: {gap.confidence}</span>
            </div>
            
            <p className="text-gray-700 mb-4">{gap.summary}</p>
            
            <div className="mb-4">
              <h4 className="font-medium text-gray-900 mb-1">Why it's a gap:</h4>
              <p className="text-gray-600 text-sm">{gap.why_it_is_a_gap}</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 p-3 rounded">
                <h4 className="font-medium text-gray-900 mb-1 text-sm">Proposed Research Questions:</h4>
                <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                  {gap.proposed_research_questions.map((q, j) => <li key={j}>{q}</li>)}
                </ul>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <h4 className="font-medium text-gray-900 mb-1 text-sm">Suggested Methodology:</h4>
                <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                  {gap.suggested_methodology.map((m, j) => <li key={j}>{m}</li>)}
                </ul>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-1 text-sm">Evidence Citations:</h4>
              <div className="text-xs text-gray-500 break-words">
                {gap.citations.join(', ')}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
