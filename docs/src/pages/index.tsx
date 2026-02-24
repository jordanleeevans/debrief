import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import Heading from "@theme/Heading";
import styles from "./index.module.css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx("hero hero--primary", styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/getting-started"
          >
            Get Started →
          </Link>
        </div>
      </div>
    </header>
  );
}

const features = [
  {
    title: "AI-Powered Stats",
    description:
      "Upload Call of Duty screenshots and let Gemini AI extract and analyze your game statistics automatically.",
  },
  {
    title: "Discord Integration",
    description:
      "Simple Discord commands (!stats, !query) let you interact with the bot right where you play.",
  },
  {
    title: "REST API",
    description:
      "A FastAPI-powered REST API with Discord OAuth and JWT authentication for accessing your match data.",
  },
];

function Feature({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center padding-horiz--md padding-vert--lg">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
