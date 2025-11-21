// Utility function to handle navigation with loading delay
export const navigateWithLoading = (path, delay = 1500) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      window.location.pathname = path;
      resolve();
    }, delay);
  });
};

// Show success message before navigation
export const showSuccessAndNavigate = (message, path, delay = 2000) => {
  // You can customize this to show a success toast or message
  console.log(`✅ ${message}`);
  return navigateWithLoading(path, delay);
};
