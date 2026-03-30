import { useState, useCallback } from "react";

function ProfilePage() {
  const [displayName, setDisplayName] = useState("Alchemist User");
  const [email, setEmail] = useState("user@notionforge.io");
  const [theme, setTheme] = useState<"dark" | "light" | "system">("dark");

  const handleSaveName = useCallback(() => {
    // Save display name (mock)
  }, []);

  const handleSaveEmail = useCallback(() => {
    // Save email (mock)
  }, []);

  const initials = displayName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="flex-1 overflow-y-auto pt-8 pb-20">
      <div className="max-w-4xl mx-auto px-10 py-4">
        {/* Header */}
        <div className="mb-12">
          <h2 className="text-4xl font-extrabold font-headline text-[#e5e2e1] tracking-tight mb-2">
            Profile
          </h2>
          <p className="text-[#c2c6d8] max-w-lg">
            Manage your account settings and preferences.
          </p>
        </div>

        {/* Avatar + Name Section */}
        <div className="bg-[#1c1b1b] rounded-xl p-8 mb-6 flex items-center gap-6">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#006de6] to-[#adc6ff] flex items-center justify-center shrink-0">
            <span className="text-2xl font-bold text-white">{initials}</span>
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-white mb-1">
              {displayName}
            </h3>
            <p className="text-sm text-gray-400">{email}</p>
          </div>
          <button
            type="button"
            className="px-4 py-2 rounded-lg border border-[#424656]/30 text-xs font-label uppercase tracking-wider text-gray-400 hover:bg-[#2a2a2a] transition-colors"
          >
            Change Avatar
          </button>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Settings */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
            {/* Display Name */}
            <div className="bg-[#1c1b1b] rounded-xl p-6">
              <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-[#adc6ff] mb-3">
                Display Name
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="flex-1 bg-transparent border-0 border-b border-[#424656]/30 py-3 text-[#e5e2e1] focus:ring-0 focus:border-[#adc6ff] transition-all placeholder:text-[#424656] outline-none"
                />
                <button
                  type="button"
                  onClick={handleSaveName}
                  className="px-4 py-2 rounded-lg bg-[#adc6ff] text-[#002e69] text-xs font-bold hover:opacity-90 transition-opacity"
                >
                  Save
                </button>
              </div>
            </div>

            {/* Email */}
            <div className="bg-[#1c1b1b] rounded-xl p-6">
              <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-[#adc6ff] mb-3">
                Email Address
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1 bg-transparent border-0 border-b border-[#424656]/30 py-3 text-[#e5e2e1] focus:ring-0 focus:border-[#adc6ff] transition-all placeholder:text-[#424656] outline-none"
                />
                <button
                  type="button"
                  onClick={handleSaveEmail}
                  className="px-4 py-2 rounded-lg bg-[#adc6ff] text-[#002e69] text-xs font-bold hover:opacity-90 transition-opacity"
                >
                  Save
                </button>
              </div>
            </div>

            {/* Theme Preference */}
            <div className="bg-[#1c1b1b] rounded-xl p-6">
              <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-[#adc6ff] mb-4">
                Theme Preference
              </label>
              <div className="flex gap-3">
                {(["dark", "light", "system"] as const).map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => setTheme(opt)}
                    className={`flex items-center gap-2 px-4 py-3 rounded-xl border text-sm transition-all ${
                      theme === opt
                        ? "border-[#adc6ff] bg-[#adc6ff]/10 text-[#adc6ff]"
                        : "border-[#424656]/30 text-gray-400 hover:border-[#424656]"
                    }`}
                  >
                    <span className="material-symbols-outlined text-sm">
                      {opt === "dark"
                        ? "dark_mode"
                        : opt === "light"
                          ? "light_mode"
                          : "contrast"}
                    </span>
                    <span className="capitalize">{opt}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* API Usage Stats */}
          <div className="col-span-12 lg:col-span-5 space-y-6">
            <div className="bg-[#353534]/40 rounded-xl p-8 border border-[#424656]/10">
              <h3 className="font-headline text-xl font-bold mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#adc6ff]">
                  analytics
                </span>
                API Usage
              </h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs text-gray-400 uppercase tracking-wider">
                      Templates Created
                    </span>
                    <span className="text-lg font-bold text-[#ffb59a]">24</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#2a2a2a] rounded-full overflow-hidden">
                    <div className="h-full bg-[#ffb59a] w-[48%] rounded-full" />
                  </div>
                  <p className="text-[10px] text-gray-500 mt-1">
                    24 / 50 this month
                  </p>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs text-gray-400 uppercase tracking-wider">
                      API Calls
                    </span>
                    <span className="text-lg font-bold text-[#adc6ff]">
                      142
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-[#2a2a2a] rounded-full overflow-hidden">
                    <div className="h-full bg-[#adc6ff] w-[28%] rounded-full" />
                  </div>
                  <p className="text-[10px] text-gray-500 mt-1">
                    142 / 500 this month
                  </p>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs text-gray-400 uppercase tracking-wider">
                      Database Rows
                    </span>
                    <span className="text-lg font-bold text-[#4edea3]">
                      387
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-[#2a2a2a] rounded-full overflow-hidden">
                    <div className="h-full bg-[#4edea3] w-[39%] rounded-full" />
                  </div>
                  <p className="text-[10px] text-gray-500 mt-1">
                    387 / 1,000 this month
                  </p>
                </div>
              </div>
            </div>

            {/* Account Section */}
            <div className="bg-[#1c1b1b] rounded-xl p-6 space-y-4">
              <h3 className="font-headline text-sm font-bold flex items-center gap-2 text-white">
                <span className="material-symbols-outlined text-sm text-gray-400">
                  manage_accounts
                </span>
                Account
              </h3>
              <div className="space-y-2">
                <button
                  type="button"
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-gray-400 hover:bg-[#2a2a2a] hover:text-white transition-all"
                >
                  <span className="material-symbols-outlined text-sm">
                    download
                  </span>
                  Export Data
                </button>
                <button
                  type="button"
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-gray-400 hover:bg-[#2a2a2a] hover:text-white transition-all"
                >
                  <span className="material-symbols-outlined text-sm">
                    key
                  </span>
                  Change Password
                </button>
                <button
                  type="button"
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-[#ffb4ab] hover:bg-[#ffb4ab]/10 transition-all"
                >
                  <span className="material-symbols-outlined text-sm">
                    delete
                  </span>
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
