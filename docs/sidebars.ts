import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebars: SidebarsConfig = {
  docsSidebar: [
    "intro",
    "getting-started",
    {
      type: "category",
      label: "Features",
      items: [
        "features/discord-commands",
        "features/rest-api",
        "features/ai-analysis",
      ],
    },
    {
      type: "category",
      label: "Architecture",
      items: ["architecture/overview", "architecture/cqrs-pattern"],
    },
    "configuration",
    "schemas",
  ],
};

export default sidebars;
