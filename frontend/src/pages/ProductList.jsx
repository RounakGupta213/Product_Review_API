import React, { useState, useEffect } from "react";
import { productApi } from "../services/api";
import { RatingDisplay } from "../components/RatingDisplay";
import { ReviewForm } from "../components/ReviewForm";
import "./ProductList.css";

export const ProductList = ({ onSelectProduct }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [reviewProductId, setReviewProductId] = useState(null);
  const [initialRating, setInitialRating] = useState(0);
  const limit = 10;

  const handleOpenReview = (productId, rating = 0) => {
    setReviewProductId(productId);
    setInitialRating(rating);
  };

  useEffect(() => {
    loadProducts();
  }, [skip]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await productApi.getProducts(skip, limit);
      setProducts(data.products);
      setTotal(data.total);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (window.confirm("Are you sure you want to delete this product?")) {
      try {
        await productApi.deleteProduct(productId);
        loadProducts();
      } catch (err) {
        setError(err.message || "Failed to delete product");
      }
    }
  };

  if (loading) return <div className="loading">Loading products...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="product-list">
      <h1>Products</h1>

      {products.length === 0 ? (
        <p className="no-products">No products available</p>
      ) : (
        <>
          <div className="products-grid">
            {products.map((product) => (
              <div key={product._id} className="product-card">
                <h3>{product.name}</h3>
                <p className="category">{product.category}</p>
                <p className="price">₹{product.price.toFixed(2)}</p>
                <RatingDisplay
                  rating={product.avg_rating}
                  totalReviews={product.total_reviews}
                  onRate={(rating) => handleOpenReview(product._id, rating)}
                />
                <div className="button-group">
                  <button
                    className="view-btn"
                    onClick={() => handleOpenReview(product._id)}
                  >
                    Add Review
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteProduct(product._id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button
              disabled={skip === 0}
              onClick={() => setSkip(Math.max(0, skip - limit))}
            >
              Previous
            </button>
            <span>
              Page {Math.floor(skip / limit) + 1} of {Math.ceil(total / limit)}
            </span>
            <button
              disabled={skip + limit >= total}
              onClick={() => setSkip(skip + limit)}
            >
              Next
            </button>
          </div>

          {reviewProductId && (
            <div className="review-modal-overlay">
              <div className="review-modal">
                <button
                  className="close-btn"
                  onClick={() => setReviewProductId(null)}
                >
                  ✕
                </button>
                <ReviewForm
                  productId={reviewProductId}
                  initialRating={initialRating}
                  onSuccess={() => {
                    setReviewProductId(null);
                    setInitialRating(0);
                    loadProducts();
                  }}
                />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
