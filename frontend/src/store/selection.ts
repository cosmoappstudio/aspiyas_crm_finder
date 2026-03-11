/**
 * Seçili markalar — Zustand store
 * /companies sayfasında kullanıcının seçtiği marka ID'leri
 */

import { create } from "zustand";

interface SelectionState {
  selectedCompanyIds: Set<string>;
  toggle: (id: string) => void;
  toggleAll: (ids: string[]) => void;
  clear: () => void;
  isSelected: (id: string) => boolean;
}

export const useSelectionStore = create<SelectionState>((set, get) => ({
  selectedCompanyIds: new Set(),

  toggle: (id) =>
    set((state) => {
      const next = new Set(state.selectedCompanyIds);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return { selectedCompanyIds: next };
    }),

  toggleAll: (ids) =>
    set((state) => {
      const allSelected = ids.every((id) => state.selectedCompanyIds.has(id));
      const next = new Set(state.selectedCompanyIds);
      if (allSelected) ids.forEach((id) => next.delete(id));
      else ids.forEach((id) => next.add(id));
      return { selectedCompanyIds: next };
    }),

  clear: () => set({ selectedCompanyIds: new Set() }),

  isSelected: (id) => get().selectedCompanyIds.has(id),
}));
