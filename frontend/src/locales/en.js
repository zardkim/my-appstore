/**
 * English Translation File
 *
 * Usage:
 * - Template: {{ $t('common.button.save') }}
 * - Script: const { t } = useI18n(); t('common.button.save')
 * - With variables: {{ $t('welcome.message', { name: username }) }}
 *
 * Structure:
 * - Nested objects (category.section.item)
 * - Clear and descriptive key names
 */

export default {
  // ============================================
  // Common UI Elements
  // ============================================
  common: {
    // Buttons
    button: {
      save: 'Save',
      saving: 'Saving...',
      cancel: 'Cancel',
      edit: 'Edit',
      delete: 'Delete',
      add: 'Add',
      search: 'Search',
      refresh: 'Refresh',
      apply: 'Apply',
      close: 'Close',
      confirm: 'Confirm',
      back: 'Back',
      backToList: 'Back to List',
      next: 'Next',
      previous: 'Previous',
      download: 'Download',
      upload: 'Upload',
      viewAll: 'View All',
      details: 'Details',
      detailedView: 'Detailed View'
    },

    // Messages
    message: {
      loading: 'Loading...',
      success: 'Successfully processed',
      error: 'An error occurred',
      noData: 'No data available',
      confirmDelete: 'Are you sure you want to delete?',
      saved: 'Saved',
      deleted: 'Deleted'
    },

    // Status
    status: {
      active: 'Active',
      inactive: 'Inactive',
      pending: 'Pending',
      approved: 'Approved',
      rejected: 'Rejected'
    },

    // General Labels
    title: 'Title',
    content: 'Content',
    category: 'Category',
    author: 'Author',
    createdDate: 'Created Date',
    status: 'Status',
    actions: 'Actions',
    username: 'Username',
    password: 'Password',
    role: 'Role',
    notAvailable: 'N/A',
    none: 'None',
    use: 'Use',

    // Authentication
    auth: {
      loginRequired: 'Login required.'
    },

    // Dark/Light Mode
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode'
  },

  // ============================================
  // Navigation
  // ============================================
  nav: {
    home: 'Home',
    discover: 'Store',
    tips: 'Tips&Tech',
    settings: 'Settings',
    more: 'More',
    favorites: 'Favorites',
    scraps: 'Scraps',
    admin: 'Admin',
    changePassword: 'Change Password',
    logout: 'Logout'
  },

  // ============================================
  // Theme
  // ============================================
  theme: {
    dark: 'Dark Mode',
    light: 'Light Mode'
  },

  // ============================================
  // Authentication
  // ============================================
  auth: {
    login: {
      title: 'Login',
      username: 'Username',
      password: 'Password',
      submit: 'Login',
      loggingIn: 'Logging in...',
      required: 'Please enter username and password',
      failed: 'Login failed. Please check your username and password.'
    },
    setup: {
      title: 'Initial Setup',
      createAdmin: 'Create Admin Account',
      welcome: 'Welcome to MyApp Store'
    }
  },

  // ============================================
  // Home/Dashboard
  // ============================================
  home: {
    title: 'Dashboard',
    welcome: 'Welcome! 👋',
    description: 'Manage your personal software library',
    recentProducts: 'Recently Added Apps',
    loading: 'Loading...',

    stats: {
      totalProducts: 'Total Products',
      totalVersions: 'Total Versions',
      lastScan: 'Last Scan',
      categoryStats: 'Category Statistics'
    },

    empty: {
      title: 'No programs registered',
      description: 'Scan programs to build your library'
    }
  },

  // ============================================
  // Product Discovery
  // ============================================
  discover: {
    title: 'App Store',
    productCount: 'programs',
    search: 'Search',
    searchPlaceholder: 'Search app name, vendor...',
    filter: 'Filter',
    categoryFilter: 'Category',
    filingRules: 'Filing Rules',
    violations: 'Scanned List',
    scan: 'Scan',

    sort: {
      latest: 'Latest',
      name: 'Name',
      category: 'Category'
    },

    category: {
      all: 'All',
      graphics: 'Graphics',
      office: 'Office',
      development: 'Development',
      utility: 'Utility',
      media: 'Media',
      os: 'OS',
      security: 'Security',
      network: 'Network',
      mac: 'Mac',
      mobile: 'Mobile',
      patch: 'Patch',
      driver: 'Driver',
      source: 'Source',
      backup: 'Backup & Recovery',
      business: 'Business',
      engineering: 'Engineering',
      theme: 'Theme & Skin',
      font: 'Font',
      uncategorized: 'Uncategorized'
    },

    noResults: {
      title: 'No search results',
      description: 'Try different keywords or filters'
    },

    modal: {
      title: 'Category'
    }
  },

  // ============================================
  // Product Detail
  // ============================================
  productDetail: {
    visit: 'Official Site',
    selectCategory: 'Select Category',
    logoSearch: 'Search Logo',
    iconHint: 'Icon (Click to search)',
    imageError: 'Failed to load image',

    form: {
      title: 'Title',
      subtitle: 'Subtitle',
      vendor: 'Vendor',
      officialWebsite: 'Official Website'
    },

    tabs: {
      info: 'Info',
      versions: 'Versions',
      screenshots: 'Screenshots',
      installation: 'Installation'
    },

    info: {
      description: 'Program Description',
      noDescription: 'No description available.',
      platform: 'Platform',
      supportSpec: 'Supported Specs',
      releaseInfo: 'Release Information',
      releaseDate: 'Release Date',
      releaseNotes: 'Release Notes',
      features: 'Key Features',
      noFeatures: 'No features information available.',
      systemRequirements: 'System Requirements',
      noSystemRequirements: 'No system requirements information available.',
      supportedFormats: 'Supported Formats',
      noFormats: 'No supported formats information available.',
      installationInfo: 'Installation Info',
      noInstallationInfo: 'No installation information available.',
      referenceSites: 'Reference Sites (for manual editing)',
      referenceSitesHint: 'Refer to these sites when manually editing metadata:'
    },

    placeholder: {
      date: 'e.g. 2024-01-15'
    },

    versions: {
      title: 'Available Versions',
      version: 'Version',
      empty: {
        title: 'No versions registered',
        description: 'No downloadable versions available yet'
      }
    },

    screenshots: {
      title: 'Screenshots',
      search: 'Search Screenshots',
      label: 'Screenshot',
      delete: 'Delete Screenshot',
      empty: {
        title: 'No screenshots',
        description: 'No screenshots collected for this product'
      }
    },

    installation: {
      title: 'Installation Guide',
      write: 'Write Guide',
      empty: {
        title: 'No installation guide',
        description: 'Click the \'Write Guide\' button above to create an installation guide'
      }
    }
  },

  // ============================================
  // Tips & Tech
  // ============================================
  tips: {
    title: '💡 Tips&Tech',
    description: 'A space for sharing useful tips and technical information',
    write: 'Write',
    scrap: 'Scrap',
    scrapped: 'Scrapped',
    views: 'Views',
    comments: 'Comments',

    filter: {
      allCategories: 'All Categories'
    },

    category: {
      tip: 'Tip',
      tech: 'Tech',
      tutorial: 'Tutorial',
      qna: 'Q&A',
      news: 'News'
    },

    sort: {
      latest: 'Latest',
      views: 'Most Viewed',
      comments: 'Most Commented'
    },

    table: {
      number: 'No.',
      views: 'Views',
      comments: 'Comments',
      createdDate: 'Date'
    },

    badge: {
      notice: 'Notice',
      new: 'NEW'
    },

    empty: {
      title: 'No posts yet',
      description: 'Write the first post!'
    },

    icon: {
      hasImage: '📷'
    }
  },

  // ============================================
  // Tips Detail
  // ============================================
  tipsDetail: {
    attachments: 'Attachments',
    comments: 'Comments',
    commentPlaceholder: 'Write a comment',
    submitComment: 'Post Comment',

    empty: {
      title: 'No comments yet',
      description: 'Be the first to comment!'
    },

    confirm: {
      deletePost: 'Are you sure you want to delete this post?',
      deleteComment: 'Are you sure you want to delete this comment?',
      deleteAttachment: 'Are you sure you want to delete this attachment?'
    },

    dialog: {
      deletePost: 'Delete Post',
      deleteComment: 'Delete Comment',
      deleteAttachment: 'Delete Attachment'
    },

    success: {
      deleted: 'Post has been deleted.',
      attachmentDeleted: 'Attachment has been deleted.'
    },

    error: {
      scrapFailed: 'Failed to scrap.',
      loadFailed: 'Failed to load post.'
    },

    validation: {
      commentRequired: 'Please enter a comment.'
    }
  },

  // ============================================
  // Tips Write
  // ============================================
  tipsWrite: {
    new: 'Write Post',
    edit: 'Edit Post',
    saveDraft: 'Save Draft',
    submit: 'Publish',
    submitEdit: 'Update',

    form: {
      category: 'Category *',
      categoryPlaceholder: 'Select a category',
      markAsNotice: 'Mark as notice',
      titlePlaceholder: 'Enter title (max 100 characters)',
      tags: 'Tags (optional)',
      tagsPlaceholder: 'Enter tags separated by comma (e.g. windows, shortcut, tip)',
      tagsHint: 'Tags help with search and categorization',
      attachments: 'Attachments (optional)'
    },

    category: {
      notice: '📢 Notice',
      tip: '💡 Tip',
      tech: '⚙️ Tech',
      tutorial: '📚 Tutorial',
      qna: '❓ Q&A',
      news: '📰 News'
    },

    file: {
      dragHint: 'Drag and drop files or click to select',
      select: 'Select Files',
      limit: 'Max 10MB, up to 5 files',
      maxFilesError: 'You can attach up to 5 files.',
      sizeError: ' is too large. Maximum',
      sizeErrorSuffix: ' allowed.',
      duplicateError: ' has already been added.'
    },

    notice: {
      title: 'Before Posting',
      item1: 'Ensure title and content are appropriate for the board',
      item2: 'Posts containing offensive language may be deleted',
      item3: 'Do not post copyrighted content'
    },

    confirm: {
      unsavedChanges: 'You have unsaved changes. Are you sure you want to leave?',
      restoreDraft: 'A draft is available. Do you want to restore it?'
    },

    success: {
      draftSaved: 'Draft saved.',
      created: 'Post has been published.',
      updated: 'Post has been updated.'
    },

    validation: {
      categoryRequired: 'Please select a category.',
      titleRequired: 'Please enter a title.',
      contentRequired: 'Please enter content.'
    }
  },

  // ============================================
  // Settings
  // ============================================
  settings: {
    title: 'Settings',

    general: {
      title: 'General Settings',
      description: 'Manage system settings',
      section: 'System Settings',
      language: 'Language'
    },

    language: {
      korean: '한국어',
      english: 'English'
    },

    network: {
      title: 'Network Settings',
      frontendUrl: 'Frontend Access URL',
      frontendUrlHint: 'Frontend access address (e.g. http://192.168.0.8:5900, http://nas.local:5900)',
      backendUrl: 'Backend API URL',
      backendUrlHint: 'Backend API address (e.g. http://192.168.0.8:8100, http://nas.local:8100)',
      corsOrigins: 'Additional Allowed Domains (CORS)',
      corsOriginsHint: 'Enter one per line. Add HTTPS URLs when using reverse proxy (NPM, Synology).'
    },

    guide: {
      title: '💡 Configuration Guide',
      localNetwork: 'Local Network Access:',
      localNetworkExample: 'Use http://internal-IP:port format (e.g. http://192.168.0.8:5900)',
      reverseProxy: 'When using Reverse Proxy:',
      reverseProxyExample: 'Add HTTPS URL configured in NPM or Synology reverse proxy',
      docker: 'Docker Environment:',
      dockerExample: 'Also update CORS_ORIGINS environment variable in docker-compose.yml',
      afterApply: 'After Applying Settings:',
      afterApplyExample: 'Backend restart may be required'
    },

    users: {
      title: 'User Management',
      description: 'Add users directly or send invitation emails',
      add: 'Add User',
      invite: 'Invite User',
      systemAdmin: 'System Administrator',

      role: {
        admin: 'Administrator',
        user: 'User'
      }
    },

    folders: {
      title: 'Folder Settings',
      description: 'Manage folder paths to scan',
      add: 'Add Folder',
      scan: 'Scan',
      scanning: 'Scanning...',
      scanThis: 'Scan This Folder',
      edit: 'Change',

      guide: {
        title: '📁 How to Add Folders',
        dockerMount: 'Docker Volume Mount:',
        dockerMountExample: '-v /path/to/your/software:/library/MyFolder',
        symbolicLink: 'Symbolic Link:',
        symbolicLinkExample: 'ln -s /path/to/your/software /library/MyFolder',
        direct: 'Direct Addition:',
        directExample: 'Add folder using button above and click \'Save\'',
        hint: '💡 Each folder can be scanned independently. Be sure to click \'Save\' after making changes.'
      },

      empty: {
        title: 'No folders registered',
        description: 'Click the \'Add Folder\' button above to add folders to scan.'
      }
    },

    categories: {
      title: 'Category Management',
      description: 'Manage program categories',
      add: 'Add Category'
    },

    board: {
      title: 'Board Management',
      description: 'Manage Tips&Tech board settings',
      categories: 'Board Categories',
      basicSettings: 'Basic Board Settings',
      postsPerPage: 'Posts per Page',
      allowComments: 'Allow Comments',
      allowCommentsHint: 'Users can comment on posts',
      allowAttachments: 'Allow Attachments',
      allowAttachmentsHint: 'Users can attach files to posts',

      postsPerPageOptions: {
        10: '10',
        20: '20',
        30: '30',
        50: '50'
      }
    },

    filingRules: {
      title: 'Filename Rules Guide',
      description: 'Check recommended filename standard rules for scanning',
      standardFormat: 'Standard Format',
      withVersion: 'Basic Format (with version)',
      formatExample1: 'ProductName.vVersion-Description.ext',
      noVersion: 'Without Version',
      formatExample2: 'ProductName-Description.ext',
      minimalFormat: 'Minimal Format',
      formatExample3: 'ProductName.vVersion.ext',
      formatExample4: 'ProductName.ext',
      correctExamples: 'Correct Examples',
      pattern1: 'Pattern 1: Complete Info',
      pattern2: 'Pattern 2: No Version',
      pattern3: 'Pattern 3: Basic Info Only',
      pattern4: 'Pattern 4: Product Name Only',
      avoidPatterns: 'Patterns to Avoid',
      avoidReason1: 'Too complex, excessive underscores',
      avoidReason2: 'Unclear product name',
      avoidReason3: 'Lowercase, confusing version separator',
      avoidReason4: 'Brackets are inconvenient',
      detailedRules: 'Detailed Rules',

      productName: {
        title: '1. Product Name',
        official: 'Official product name',
        caseInsensitive: 'use (case-sensitive)',
        spaces: 'Spaces allowed',
        specialChars: 'Avoid special characters (',
        excluded: 'excluded)'
      },

      version: {
        title: '2. Version',
        prefix: '.v',
        prefixRequired: 'prefix required',
        dotOnly: 'Numbers and dots (',
        dotOnlySuffix: ') only',
        yearAsVersion: 'Years are considered versions (2023, 2024, etc.)',
        missingV: '(missing v)',
        notNumeric: '(not numeric)'
      },

      description: {
        title: '3. Description',
        separator: '-',
        separatorUse: 'separator',
        concise: 'Keep it concise',
        multiple: 'Separate multiple info with comma or space'
      },

      conversionExamples: 'Conversion Examples',
      oldFilename: 'Old Filename',
      standardFormatColumn: 'Standard Format',

      checklist: {
        title: 'Pre-Upload Checklist',
        productName: 'Is product name official?',
        version: 'If version exists,',
        versionFormat: 'format?',
        description: 'If description exists,',
        descriptionStart: 'does it start with?',
        underscore: 'Underscores (',
        underscoreChange: ') replaced with spaces?',
        extension: 'Is extension lowercase?',
        concise: 'Is filename concise? (unnecessary info removed)'
      },

      quickReference: 'Quick Reference',
      quickRef: {
        full: 'Full Format:',
        noVersion: 'No Version:',
        basic: 'Basic Format:',
        minimal: 'Minimal Format:'
      },

      example: 'Example:'
    },

    metadata: {
      title: 'Metadata Settings',
      description: 'Manage AI-based metadata generation settings',
      test: 'Test Metadata',
      scanMode: 'Scan Mode',
      aiOnly: '🤖 AI Only',
      aiOnlyDescription: 'Use AI models only to generate metadata',
      modelSettings: 'AI Model Settings',
      provider: 'AI Provider',

      openaiModel: 'OpenAI Model',
      o1Series: 'o1 Series (Latest Reasoning Models)',
      o1: {
        latest: 'o1 (Paid - Latest Reasoning)',
        preview: 'o1 Preview (Paid - Preview)',
        mini: 'o1 Mini (Paid - Fast)'
      },

      gpt4o: 'GPT-4o (Recommended)',
      gpt4oMini: 'GPT-4o Mini (Paid - Cheap, Recommended)',
      gpt4oLatest: 'GPT-4o (Paid - Latest)',
      gpt4o20241120: 'GPT-4o (2024-11-20) (Paid)',
      gpt4o20240806: 'GPT-4o (2024-08-06) (Paid)',
      gpt4o20240513: 'GPT-4o (2024-05-13) (Paid)',

      gpt4Turbo: 'GPT-4 Turbo',
      gpt4Turbo20240409: 'GPT-4 Turbo (2024-04-09) (Paid)',
      gpt4TurboPreview: 'GPT-4 Turbo Preview (Paid)',

      legacyModels: 'Legacy Models',
      gpt4: 'GPT-4 (Paid)',
      gpt40613: 'GPT-4 (0613) (Paid)',

      openaiHint: '💡 GPT-4o Mini offers best price-to-performance ratio. o1 is suitable for complex reasoning tasks.',

      geminiModel: 'Gemini Model',
      gemini3: 'Gemini 3 (Latest Preview) 🚀',
      gemini3ProPreview: 'Gemini 3 Pro Preview (High Performance)',
      gemini25: 'Gemini 2.5 (Stable) ⭐ Recommended',
      gemini25Flash: 'Gemini 2.5 Flash (Free - Stable)',
      gemini25Pro: 'Gemini 2.5 Pro (Free - High Performance)',
      gemini25FlashLite: 'Gemini 2.5 Flash Lite (Lightweight)',
      previousVersions: 'Previous Versions',
      gemini20FlashLite: 'Gemini 2.0 Flash Lite (Lightweight)',

      geminiHint: '💡 Gemini 2.5 Flash is stable and has generous quota. (Recommended)',
      geminiWarning: '⚠️ 429 error may occur when free quota is exceeded.',

      geminiApiKey: 'Gemini API Key',
      geminiApiKeyFrom: 'Get Gemini API Key from',
      openaiApiKey: 'OpenAI API Key',
      openaiApiKeyFrom: 'Get OpenAI API Key from',
      apiKeyFrom: '',
      apiKeyFromSuffix: '',

      pricing: {
        title: '💰 Pricing Information',
        openai: 'OpenAI (All Paid):',
        o1: 'o1: $15/1M input, $60/1M output (Advanced Reasoning)',
        gpt4oMini: 'GPT-4o Mini: $0.15/1M input, $0.60/1M output (Cheapest, Recommended)',
        gpt4o: 'GPT-4o: $2.50/1M input, $10.00/1M output',
        gpt4Turbo: 'GPT-4 Turbo: $10/1M input, $30/1M output',
        gpt4: 'GPT-4: $30/1M input, $60/1M output',
        gemini: 'Gemini (Free Quota Available ⭐):',
        free: 'Free Quota: 15 requests/min, 1,500 requests/day',
        gemini3: 'Gemini 3.0 Flash Exp: Free (Latest)',
        gemini25: 'Gemini 2.5 Flash Exp: Free (Stable, Recommended)',
        gemini25Pro: 'Gemini 2.5 Pro Exp: Free (High Performance)'
      }
    },

    googleSearch: {
      title: '🔍 Google Custom Search API Settings',
      description: 'Google Custom Search API key and Search Engine ID are required for image search.',
      apiKey: 'Google Custom Search API Key',
      apiKeyHint: 'Enable Custom Search JSON API in Google Cloud Console and generate an API key.',
      getApiKey: 'Get API Key →',
      searchEngineId: 'Search Engine ID',
      searchEngineIdHint: '(cx parameter)',
      searchEngineIdDescription: 'Create a search engine with image search enabled in Programmable Search Engine and copy the ID.',
      createSearchEngine: 'Create Search Engine →',

      guide: {
        title: '💡 Configuration Guide',
        step1: '1. Generate API Key:',
        step1: {
          item1: 'Google Cloud Console → APIs & Services → Credentials',
          item2: 'Enable \'Custom Search JSON API\'',
          item3: 'Create API Key'
        },
        step2: '2. Create Search Engine:',
        step2: {
          item1: 'Go to Programmable Search Engine page',
          item2: 'Create new search engine (search entire web)',
          item3: 'Enable \'Image search\'',
          item4: 'Copy search engine ID (cx parameter)'
        }
      },

      freeQuota: 'Free Quota:',
      freeQuotaDetails: '100 searches per day'
    },

    customPrompt: {
      title: '📝 Custom Prompts',
      description: 'Customize prompts for AI queries',
      variables: '💡 Available Variables:',
      softwareName: '{software_name}',
      softwareNameDesc: '- Automatically replaced with software name',
      tip: 'Tip: More detailed and specific questions help AI provide more accurate information.',
      openai: 'OpenAI Prompt',
      gemini: 'Gemini Prompt',
      restoreDefault: 'Restore Default',
      charCount: 'Character Count:',
      enableHint: 'Check the \'Use\' checkbox above to use custom prompts.',

      placeholder: {
        openai: 'Enter prompt for OpenAI...',
        gemini: 'Enter prompt for Gemini...'
      }
    },

    scanExceptions: {
      title: '🚫 Scan Exceptions',
      description: 'Configure files and folders to exclude from scanning',
      files: '📄 File Patterns',
      filesHint: 'Enter file patterns to exclude. Wildcards (*) supported.',
      filesPlaceholder: 'e.g. *.txt, *.log, Thumbs.db'
    }
  },

  // ============================================
  // Admin
  // ============================================
  admin: {
    title: 'System Management',
    description: 'File scanning and scheduler configuration',
    scanPrograms: 'Scan Programs',

    tabs: {
      manualScan: 'Manual Scan',
      scheduler: 'Auto Scan Scheduler',
      unmatched: 'Unmatched List'
    },

    manualScan: {
      title: 'Manual File Scan',
      useAI: 'Enable AI Metadata Generation (OpenAI API required)',
      benefit1: '✓ Auto-generate accurate program names, descriptions, vendors',
      benefit2: '✓ Auto-categorize appropriately',
      benefit3: '✓ Download and cache official icons',
      pathPlaceholder: '/mnt/software',
      start: 'Start Scan',
      scanning: 'Scanning...',
      complete: '✓ Scan Complete',
      newProducts: 'New Programs:',
      count: '',
      newVersions: 'New Versions:',
      updatedProducts: 'Updated Programs:',
      aiGenerated: 'AI Metadata Generated:',
      iconsCached: 'Icons Cached:',
      errors: 'Errors:',
      errorDetails: 'View Error Details'
    },

    unmatched: {
      stats: {
        total: 'Total',
        pending: 'Pending',
        approved: 'Approved',
        manual: 'Manual',
        ignored: 'Ignored'
      },

      filter: {
        label: 'Status Filter:',
        all: 'All',
        pending: 'Pending',
        approved: 'Approved',
        manual: 'Manual',
        ignored: 'Ignored'
      },

      table: {
        filename: 'Filename',
        parsedName: 'Parsed Name',
        confidence: 'Confidence',
        aiSuggestion: 'AI Suggestion'
      },

      status: {
        pending: 'Pending',
        approved: 'Approved',
        manual: 'Manual',
        ignored: 'Ignored'
      },

      noItemsFiltered: 'No items with this status.',
      noItems: 'No unmatched items.',
      hint: 'Items with less than 90% confidence during scan will appear here.'
    },

    info: {
      title: 'System Information',
      phase: '🚀 Phase 2 Features Activated',
      parsingAlgorithm: 'Filename Parsing Algorithm',
      parsingAlgorithmDesc: 'Auto-extract software name, version, vendor from filenames',
      aiMetadata: 'AI Metadata Generation',
      aiMetadataDesc: 'Use OpenAI GPT to generate accurate descriptions, vendors, categories',
      iconCaching: 'Icon Download & Caching',
      iconCachingDesc: 'Automatically find and cache official icons locally',
      fallback: 'Fallback Mechanism',
      fallbackDesc: 'Auto-fallback to parsed info when AI API key is missing or errors occur',

      tips: '💡 Usage Tips',
      tipSetupOpenAI: 'To set up OpenAI API key,',
      tipSetupOpenAISuffix: 'set OPENAI_API_KEY in file',
      tipWithoutAI: 'Works with basic metadata even without AI features',
      tipFolderName: 'Clearer folder names lead to more accurate metadata'
    }
  },

  // ============================================
  // Categories
  // ============================================
  category: {
    Graphics: 'Graphics',
    Office: 'Office',
    Development: 'Development',
    Utility: 'Utility',
    Media: 'Media',
    OS: 'OS',
    Security: 'Security',
    Network: 'Network',
    Mac: 'Mac',
    Mobile: 'Mobile',
    Patch: 'Patch',
    Driver: 'Driver',
    Source: 'Source',
    Backup: 'Backup',
    Business: 'Business',
    Engineering: 'Engineering',
    Theme: 'Theme',
    Hardware: 'Hardware',
    Uncategorized: 'Uncategorized'
  },

  // ============================================
  // Favorites
  // ============================================
  favorites: {
    title: '❤️ Favorites',
    description: 'Your favorited programs',
    remove: 'Remove from Favorites',
    goToStore: 'Go to Store',

    empty: {
      title: 'No favorites yet',
      description: 'Add programs you like from the store to favorites'
    }
  },

  // ============================================
  // Scraps
  // ============================================
  scraps: {
    title: '📌 Scraps',
    description: 'Your scrapped Tips&Tech posts',
    goToTips: 'Go to Tips&Tech',

    table: {
      scrapDate: 'Scrap Date'
    },

    empty: {
      title: 'No scraps yet',
      description: 'Scrap useful posts from Tips&Tech board'
    }
  },

  // ============================================
  // Change Password
  // ============================================
  changePassword: {
    title: 'Change Password',
    description: 'Change your password regularly for security',
    submit: 'Change Password',
    submitting: 'Changing...',
    warning: 'Changing password will log you out from all devices. You will need to login again with the new password.',

    form: {
      currentPassword: 'Current Password *',
      currentPasswordPlaceholder: 'Enter current password',
      newPassword: 'New Password *',
      newPasswordPlaceholder: 'Enter new password (min 4 characters)',
      minLengthHint: 'Password must be at least 4 characters',
      confirmPassword: 'Confirm New Password *',
      confirmPasswordPlaceholder: 'Re-enter new password'
    },

    validation: {
      mismatch: 'New passwords do not match.',
      minLength: 'Password must be at least 4 characters.',
      same: 'New password is same as current password.'
    },

    success: {
      changed: 'Password has been changed successfully.'
    },

    error: {
      wrongPassword: 'Current password is incorrect.',
      failed: 'Failed to change password. Please try again.'
    },

    guide: {
      title: 'Password Security Tips',
      tip1: 'Use a password that is difficult to guess',
      tip2: 'Use a different password from other services',
      tip3: 'Change your password regularly'
    }
  },

  // ============================================
  // Filename Violations
  // ============================================
  filenameViolations: {
    title: 'Scanned List',
    subtitle: 'List of scanned files',

    // Statistics
    stats: {
      total: 'Total Items',
      scanned: 'Scanned Items',
      mismatched: 'Mismatched Items'
    },

    // Action buttons
    actions: {
      selectAll: 'Select All',
      deselectAll: 'Deselect All',
      batchRename: 'Batch Rename Selected',
      refresh: 'Refresh',
      applySuggestion: 'Apply Suggestion',
      editFilename: 'Edit Filename',
      markResolved: 'Mark as Resolved',
      delete: 'Delete',
      aiMatching: 'Generate AI Metadata'
    },

    // Violation types
    violationType: {
      underscore_overuse: 'Excessive Underscores',
      bracket_usage: 'Bracket Usage',
      version_format: 'Invalid Version Format',
      lowercase_name: 'Lowercase Only',
      complex_name: 'Complex Filename',
      invalid_chars: 'Special Characters'
    },

    // Editing mode
    editing: {
      title: 'Editing Filename',
      placeholder: 'Enter new filename',
      save: 'Save',
      cancel: 'Cancel'
    },

    // Messages
    messages: {
      noViolations: 'No scanned files',
      allMatching: 'No scanned files',
      renameSuccess: 'Filename changed successfully.\nClick the AI Matching button to update metadata.',
      renameConfirm: 'Change to "{{name}}"?',
      batchRenameConfirm: 'Rename {{count}} selected items with suggested filenames?',
      deleteConfirm: 'Delete this item?',
      aiMatchingConfirm: 'Regenerate metadata with AI?',
      aiMatchingSuccess: 'Metadata updated successfully.\nRedirecting to store page.',
      selectItemsFirst: 'Please select items to change.',
      noSuggestion: 'No suggested filename available.',
      enterFilename: 'Please enter a filename.',
      productIdNotFound: 'Product ID not found.',
      batchRenameHint: '\n\nClick the AI Matching button to update metadata.'
    },

    // Item information
    item: {
      problem: 'Problem:',
      suggestion: 'Suggestion:',
      discoveredAt: 'Discovered at:'
    }
  },

  // ============================================
  // Footer
  // ============================================
  footer: {
    copyright: 'All rights reserved.',
    subtitle: 'Personal Software Library Management System'
  }
}
