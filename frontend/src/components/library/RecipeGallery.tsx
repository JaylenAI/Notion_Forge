import { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";

interface Recipe {
  readonly id: string;
  readonly name: string;
  readonly name_en: string;
  readonly description: string;
  readonly description_en: string;
  readonly category: string;
  readonly icon: string;
  readonly author: string;
  readonly tags: readonly string[];
  readonly complexity: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  business: "bg-blue-900/50 text-blue-300",
  personal: "bg-pink-900/50 text-pink-300",
  general: "bg-gray-700/50 text-gray-300",
};

const COMPLEXITY_LABELS: Record<string, { label: string; color: string }> = {
  simple: { label: "Simple", color: "text-green-400" },
  standard: { label: "Standard", color: "text-blue-400" },
  advanced: { label: "Advanced", color: "text-purple-400" },
};

function RecipeGallery() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [importing, setImporting] = useState<string | null>(null);

  useEffect(() => {
    fetchRecipes();
  }, [category, search]);

  const fetchRecipes = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (category) params.set("category", category);
      if (search) params.set("search", search);
      const resp = await fetch(`${API_URL}/api/recipes?${params}`);
      const data = await resp.json();
      setRecipes(data.recipes ?? []);
    } catch {
      setRecipes([]);
    } finally {
      setLoading(false);
    }
  }, [category, search]);

  const handleUseRecipe = async (recipeId: string) => {
    setImporting(recipeId);
    try {
      // Fetch full recipe with blueprint
      const resp = await fetch(`${API_URL}/api/recipes/${recipeId}`);
      const data = await resp.json();
      if (!data.blueprint) {
        toast.error("Recipe has no blueprint");
        return;
      }
      // Import blueprint
      const importResp = await fetch(`${API_URL}/api/templates/blueprint/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data.blueprint),
      });
      const result = await importResp.json();
      if (result.success) {
        toast.success(`Created! ${result.summary.pages} pages, ${result.summary.databases} DBs`);
        if (result.notion_url) window.open(result.notion_url, "_blank");
      } else {
        toast.error("Import failed");
      }
    } catch {
      toast.error("Failed to use recipe");
    } finally {
      setImporting(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Search & Filter */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-base text-gray-500">
            search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search recipes..."
            className="w-full bg-[var(--surface-variant,#353534)] border-none rounded-xl text-sm text-[var(--text-primary,#e5e2e1)] placeholder:text-gray-500 pl-10 pr-4 py-2.5 outline-none focus:ring-1 focus:ring-[#adc6ff]"
          />
        </div>
        <div className="flex gap-1.5">
          {["", "business", "personal"].map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${
                category === cat
                  ? "bg-[#adc6ff]/20 text-[#adc6ff]"
                  : "text-gray-400 hover:text-gray-200 hover:bg-[#2a2a2a]"
              }`}
            >
              {cat === "" ? "All" : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Recipe Grid */}
      {loading ? (
        <div className="text-center text-gray-500 py-12">Loading recipes...</div>
      ) : recipes.length === 0 ? (
        <div className="text-center text-gray-500 py-12">
          <span className="material-symbols-outlined text-4xl mb-2 block">recipe</span>
          <p>No recipes found</p>
          <p className="text-xs mt-1">Add .json files to the recipes/ directory</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {recipes.map((recipe) => (
            <div
              key={recipe.id}
              className="bg-[var(--surface-variant,#1e1e1e)] rounded-2xl border border-[var(--border-color,#333)] p-5 hover:border-[#adc6ff]/30 transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{recipe.icon}</span>
                  <div>
                    <h3 className="font-bold text-[var(--text-primary,#e5e2e1)] text-sm">{recipe.name}</h3>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${CATEGORY_COLORS[recipe.category] ?? CATEGORY_COLORS.general}`}>
                      {recipe.category}
                    </span>
                  </div>
                </div>
                <span className={`text-[10px] ${COMPLEXITY_LABELS[recipe.complexity]?.color ?? "text-gray-400"}`}>
                  {COMPLEXITY_LABELS[recipe.complexity]?.label ?? recipe.complexity}
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-3 line-clamp-2">{recipe.description}</p>
              <div className="flex flex-wrap gap-1 mb-3">
                {recipe.tags.slice(0, 4).map((tag) => (
                  <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-[#2a2a2a] text-gray-400">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-gray-500">by {recipe.author}</span>
                <button
                  type="button"
                  onClick={() => handleUseRecipe(recipe.id)}
                  disabled={importing === recipe.id}
                  className="px-3 py-1.5 rounded-lg bg-[#adc6ff]/10 text-[#adc6ff] text-xs hover:bg-[#adc6ff]/20 transition-colors disabled:opacity-50"
                >
                  {importing === recipe.id ? "Creating..." : "Use Template"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecipeGallery;
