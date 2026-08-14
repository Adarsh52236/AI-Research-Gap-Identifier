import { create } from 'zustand';

const useAppStore = create((set) => ({
  query: '',
  setQuery: (query) => set({ query }),

  results: [],
  setResults: (results) => set({ results }),

  selectedPaperIds: [],
  togglePaperSelection: (paperId) => set((state) => {
    const isSelected = state.selectedPaperIds.includes(paperId);
    if (isSelected) {
      return { selectedPaperIds: state.selectedPaperIds.filter((id) => id !== paperId) };
    } else {
      return { selectedPaperIds: [...state.selectedPaperIds, paperId] };
    }
  }),
  selectAllPapers: (paperIds) => set({ selectedPaperIds: paperIds }),
  clearSelection: () => set({ selectedPaperIds: [] }),

  downloads: {}, // paper_id -> local_path
  setDownload: (paperId, localPath) => set((state) => ({
    downloads: { ...state.downloads, [paperId]: localPath },
  })),

  extractions: {}, // paper_id -> sections_found
  setExtraction: (paperId, sections) => set((state) => ({
    extractions: { ...state.extractions, [paperId]: sections },
  })),

  report: null,
  setReport: (reportData) => set({ report: reportData }),
}));

export default useAppStore;
