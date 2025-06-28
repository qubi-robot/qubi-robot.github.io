const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Qubi Protocol',
  tagline: 'Modular Social Robot Communication Protocol',
  favicon: 'img/favicon.ico',

  url: 'https://qubi-robot.github.io',
  baseUrl: '/',

  organizationName: 'qubi-robot',
  projectName: 'qubi-robot.github.io',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ja'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/qubi-robot/qubi-robot.github.io/tree/main/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],


  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/qubi-social-card.jpg',
      navbar: {
        title: 'Qubi Protocol',
        logo: {
          alt: 'Qubi Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            href: 'https://github.com/qubi-robot/qubi-robot.github.io',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/intro',
              },
              {
                label: 'API Reference',
                to: '/docs/api-reference/arduino',
              },
              {
                label: 'Tutorials',
                to: '/docs/tutorials/custom-module',
              },
            ],
          },
          {
            title: 'Libraries',
            items: [
              {
                label: 'Arduino/ESP32',
                to: '/docs/api-reference/arduino',
              },
              {
                label: 'TypeScript',
                to: '/docs/api-reference/typescript',
              },
              {
                label: 'Python',
                to: '/docs/api-reference/python',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/qubi-robot/qubi-robot.github.io',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Qubi Project. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['arduino', 'json', 'python', 'typescript'],
      },
    }),
};

module.exports = config;