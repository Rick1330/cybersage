module.exports = {
  docs: [
    {
      type: 'doc',
      id: 'index', // Assuming index.md is the Introduction
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Architecture',
      items: ['architecture/README'], // Path relative to docs/src
    },
    {
      type: 'category',
      label: 'Security',
      items: ['security/README'], // Path relative to docs/src
    },
    {
      type: 'category',
      label: 'Developer Guide',
      items: [
        'developer_guide/README', // Existing overview
        {
          type: 'category',
          label: 'Core Engine',
          link: { type: 'doc', id: 'developer_guide/core/index' }, // Link to the new overview page
          items: [
            'developer_guide/core/agent_manager',
            'developer_guide/core/chain_builder',
            'developer_guide/core/context_manager',
            'developer_guide/core/prompt_templates',
          ],
        },
        // ... other items or categories in Developer Guide
      ],
    },
    {
      type: 'category',
      label: 'User Guide',
      items: ['user_guide/README'], // Path relative to docs/src - will allow nesting
    },
    {
      type: 'category',
      label: 'API Reference',
      items: ['api_reference/README'], // Path relative to docs/src
    },
    {
      type: 'category',
      label: 'Operations Guide',
      items: ['operations_guide/README'], // Path relative to docs/src
    },
    {
      type: 'doc',
      id: 'contributing', // Will create this file later
      label: 'Contributing',
    },
  ],
};
