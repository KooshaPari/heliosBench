import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'HeliosBench',
  description: 'Benchmark CLI tools with resource tracking, leak detection, and comparison runs.',
  cleanUrls: true,
  head: [['meta', { name: 'theme-color', content: '#0f172a' }]],
  themeConfig: {
    nav: [
      { text: 'Getting Started', link: '/getting-started' },
      { text: 'Tasks', link: '/tasks' },
      { text: 'Metrics', link: '/metrics' },
    ],
    sidebar: {
      '/': [
        {
          text: 'Overview',
          items: [
            { text: 'Getting Started', link: '/getting-started' },
            { text: 'Tasks', link: '/tasks' },
            { text: 'Metrics', link: '/metrics' },
          ],
        },
      ],
    },
    outline: { level: [2, 3] },
    socialLinks: [{ icon: 'github', link: 'https://github.com/laude-institute/terminal-bench' }],
  },
})
