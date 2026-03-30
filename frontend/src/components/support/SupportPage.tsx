import { useState, useCallback } from "react";

interface FaqItem {
  readonly question: string;
  readonly answer: string;
}

const FAQ_ITEMS: readonly FaqItem[] = [
  {
    question: "How do I connect NotionForge to my Notion workspace?",
    answer:
      "Go to the Integrations page, enter your Notion Integration Token, and provide your target page URL. Click 'Save & Connect' to establish the bridge. Make sure your integration has 'Insert Content' and 'Read Content' permissions enabled.",
  },
  {
    question: "What types of templates can AI generate?",
    answer:
      "NotionForge can create project dashboards, task boards, CRM databases, content calendars, meeting notes systems, knowledge bases, and more. Simply describe what you need in the chat, and the AI will design the optimal structure.",
  },
  {
    question: "Is my Notion API key stored securely?",
    answer:
      "Your API key is stored locally in your browser's localStorage and is sent directly to the Notion API. It is never stored on our servers or shared with third parties.",
  },
  {
    question: "Can I customize the generated templates after creation?",
    answer:
      "Absolutely. Once the template is created in your Notion workspace, you have full control. You can modify properties, views, layouts, and content directly in Notion.",
  },
  {
    question: "What should I do if template generation fails?",
    answer:
      "Check that your Integration Token is valid, your target page has the integration connected, and the integration has proper permissions. You can test the connection on the Integrations page.",
  },
];

interface DocLink {
  readonly title: string;
  readonly description: string;
  readonly icon: string;
  readonly href: string;
  readonly external?: boolean;
}

const DOC_LINKS: readonly DocLink[] = [
  {
    title: "Getting Started",
    description: "Set up NotionForge and create your first template in under 5 minutes.",
    icon: "rocket_launch",
    href: "#getting-started",
  },
  {
    title: "Skill Development Guide",
    description: "Learn how to build custom skills and extend NotionForge capabilities.",
    icon: "school",
    href: "/docs/SKILL_GUIDE.md",
    external: true,
  },
  {
    title: "API Reference",
    description: "Complete reference for the NotionForge REST and WebSocket APIs.",
    icon: "api",
    href: "#api-reference",
  },
  {
    title: "GitHub Repository",
    description: "View the source code, report issues, and contribute to the project.",
    icon: "code",
    href: "https://github.com/notionforge/notionforge",
    external: true,
  },
];

function FaqToggle({ item }: { readonly item: FaqItem }) {
  const [open, setOpen] = useState(false);

  const handleToggle = useCallback(() => {
    setOpen((prev) => !prev);
  }, []);

  return (
    <div className="border border-[#424656]/10 rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={handleToggle}
        className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-[#1c1b1b] transition-colors"
      >
        <span className="text-sm font-medium text-[#e5e2e1] pr-4">
          {item.question}
        </span>
        <span
          className={`material-symbols-outlined text-[#adc6ff] text-sm shrink-0 transition-transform duration-200 ${
            open ? "rotate-180" : ""
          }`}
        >
          expand_more
        </span>
      </button>
      {open && (
        <div className="px-6 pb-4 animate-fade-in">
          <p className="text-sm text-gray-400 leading-relaxed">{item.answer}</p>
        </div>
      )}
    </div>
  );
}

function SupportPage() {
  return (
    <div className="flex-1 overflow-y-auto pt-8 pb-20">
      <div className="max-w-5xl mx-auto px-10 py-4">
        {/* Header */}
        <div className="mb-12">
          <h2 className="text-4xl font-extrabold font-headline text-[#e5e2e1] tracking-tight mb-2">
            Support & Documentation
          </h2>
          <p className="text-[#c2c6d8] max-w-lg">
            Find answers, explore guides, and get help with NotionForge.
          </p>
        </div>

        <div className="grid grid-cols-12 gap-8">
          {/* Get Help - FAQ */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-[#ffb59a]">
                  help
                </span>
                <h3 className="text-xl font-bold font-headline text-white">
                  Get Help
                </h3>
              </div>
              <div className="space-y-3">
                {FAQ_ITEMS.map((item) => (
                  <FaqToggle key={item.question} item={item} />
                ))}
              </div>
            </div>

            {/* Contact Section */}
            <div className="bg-[#1c1b1b] rounded-xl p-8 mt-8">
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-[#4edea3]">
                  mail
                </span>
                <h3 className="text-xl font-bold font-headline text-white">
                  Contact Us
                </h3>
              </div>
              <p className="text-sm text-gray-400 mb-6">
                Can&apos;t find what you&apos;re looking for? Reach out to our team.
              </p>
              <div className="grid grid-cols-2 gap-4">
                <a
                  href="mailto:support@notionforge.io"
                  className="glass-panel p-4 rounded-xl border border-[#424656]/10 hover:border-[#adc6ff]/20 transition-all flex items-center gap-3"
                >
                  <span className="material-symbols-outlined text-[#adc6ff]">
                    email
                  </span>
                  <div>
                    <p className="text-sm font-bold text-white">Email</p>
                    <p className="text-xs text-gray-400">
                      support@notionforge.io
                    </p>
                  </div>
                </a>
                <a
                  href="https://github.com/notionforge/notionforge/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="glass-panel p-4 rounded-xl border border-[#424656]/10 hover:border-[#adc6ff]/20 transition-all flex items-center gap-3"
                >
                  <span className="material-symbols-outlined text-[#ffb59a]">
                    bug_report
                  </span>
                  <div>
                    <p className="text-sm font-bold text-white">Bug Report</p>
                    <p className="text-xs text-gray-400">GitHub Issues</p>
                  </div>
                </a>
              </div>
            </div>
          </div>

          {/* Documentation Links */}
          <div className="col-span-12 lg:col-span-5" id="docs">
            <div className="bg-[#353534]/40 rounded-xl p-8 border border-[#424656]/10">
              <div className="flex items-center gap-2 mb-6">
                <span className="material-symbols-outlined text-[#adc6ff]">
                  menu_book
                </span>
                <h3 className="text-xl font-bold font-headline text-white">
                  Documentation
                </h3>
              </div>
              <div className="space-y-4">
                {DOC_LINKS.map((doc) => (
                  <a
                    key={doc.title}
                    href={doc.href}
                    target={doc.external ? "_blank" : undefined}
                    rel={doc.external ? "noopener noreferrer" : undefined}
                    className="block p-4 rounded-xl bg-[#1c1b1b] border border-[#424656]/10 hover:border-[#adc6ff]/20 transition-all group"
                  >
                    <div className="flex items-start gap-3">
                      <span className="material-symbols-outlined text-[#adc6ff] mt-0.5">
                        {doc.icon}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-sm text-white group-hover:text-[#adc6ff] transition-colors">
                            {doc.title}
                          </h4>
                          {doc.external && (
                            <span className="material-symbols-outlined text-[10px] text-gray-500">
                              open_in_new
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                          {doc.description}
                        </p>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            </div>

            {/* Quick Tips */}
            <div className="bg-[#1c1b1b] rounded-xl p-6 mt-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-[#ffb59a]">
                  tips_and_updates
                </span>
                <h4 className="font-bold text-sm text-white">Quick Tips</h4>
              </div>
              <ul className="space-y-3">
                <li className="flex items-start gap-2 text-xs text-gray-400">
                  <span className="text-[#4edea3] mt-0.5">*</span>
                  Be specific about database properties you want when describing templates.
                </li>
                <li className="flex items-start gap-2 text-xs text-gray-400">
                  <span className="text-[#4edea3] mt-0.5">*</span>
                  You can ask the AI to include sample data by mentioning it in your prompt.
                </li>
                <li className="flex items-start gap-2 text-xs text-gray-400">
                  <span className="text-[#4edea3] mt-0.5">*</span>
                  Use the Library page to browse and re-use previously generated templates.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SupportPage;
