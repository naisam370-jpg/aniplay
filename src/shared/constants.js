module.exports = {
  APP_NAME: 'AniPlay',
  APP_VERSION: '1.0.0',
  
  // Video formats supported
  SUPPORTED_FORMATS: [
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm',
    'm4v', '3gp', 'ogv', 'ts', 'mpg', 'mpeg', 'm2v'
  ],
  
  // UI constants
  DEFAULT_VOLUME: 70,
  SEEK_STEP: 10, // seconds
  GRID_SIZES: {
    SMALL: 150,
    MEDIUM: 200,
    LARGE: 250
  },
  
  // Paths
  LIBRARY_PATH: './anime-library',
  COVERS_PATH: './covers',
  DATA_PATH: './data'
};
