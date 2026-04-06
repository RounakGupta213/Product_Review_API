const API_BASE_URL = "http://localhost:8000/api/v1";

// Product API calls
export const productApi = {
  // Create product
  createProduct: async (productData) => {
    const response = await fetch(`${API_BASE_URL}/products`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(productData),
    });
    if (!response.ok) throw new Error("Failed to create product");
    return response.json();
  },

  // Get all products
  getProducts: async (skip = 0, limit = 10) => {
    const response = await fetch(
      `${API_BASE_URL}/products?skip=${skip}&limit=${limit}`
    );
    if (!response.ok) throw new Error("Failed to fetch products");
    return response.json();
  },

  // Get product by ID
  getProduct: async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`);
    if (!response.ok) throw new Error("Failed to fetch product");
    return response.json();
  },

  // Update product
  updateProduct: async (productId, productData) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(productData),
    });
    if (!response.ok) throw new Error("Failed to update product");
    return response.json();
  },

  // Delete product
  deleteProduct: async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete product");
  },
};

// Review API calls
export const reviewApi = {
  // Create review for a product
  createReview: async (productId, reviewData) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}/reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reviewData),
    });
    if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: "Failed to create review" }));
        throw new Error(data.detail || "Failed to create review");
    }
    return response.json();
  },

  // Get reviews for a product
  getProductReviews: async (productId, skip = 0, limit = 10) => {
    const response = await fetch(
      `${API_BASE_URL}/products/${productId}/reviews?skip=${skip}&limit=${limit}`
    );
    if (!response.ok) throw new Error("Failed to fetch reviews");
    return response.json();
  },

  // Delete review 
  deleteReview: async (reviewId, userId) => {
    const response = await fetch(
      `${API_BASE_URL}/reviews/${reviewId}?user_id=${userId}`,
      { method: "DELETE" }
    );
    if (!response.ok) throw new Error("Failed to delete review");
  },
};
