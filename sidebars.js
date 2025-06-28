/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/first-robot',
      ],
    },
    {
      type: 'category',
      label: 'Protocol',
      items: [
        'protocol/overview',
        'protocol/message-format',
        'protocol/error-handling',
      ],
    },
    {
      type: 'category',
      label: 'Modules',
      items: [
        'modules/actuator',
        'modules/display',
        'modules/mobile',
        'modules/sensor',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api-reference/arduino',
        'api-reference/typescript',
        'api-reference/python',
      ],
    },
    {
      type: 'category',
      label: 'Tutorials',
      items: [
        'tutorials/custom-module',
        'tutorials/web-interface',
        'tutorials/advanced-patterns',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/guidelines',
        'contributing/code-style',
      ],
    },
  ],
};

module.exports = sidebars;