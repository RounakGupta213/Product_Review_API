import React, { useState, useEffect } from "react";
import { productApi, reviewApi } from "../services/api";
import { RatingDisplay } from "../components/RatingDisplay";
import { ReviewForm } from "../components/ReviewForm";
import { ReviewItem } from "../components/ReviewItem";
import "./ProductDetail.css";

export const ProductDetail = ({ productId, onBack }) => {
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [initialRating, setInitialRating] = useState(0);

  useEffect(() => {
    loadProductAndReviews();
  }, [productId]);

  const loadProductAndReviews = async () => {
    try {
      setLoading(true);
      const [productData, reviewsData] = await Promise.all([
        productApi.getProduct(productId),
        reviewApi.getProductReviews(productId),
      ]);
      setProduct(productData);
      setReviews(reviewsData.reviews);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to load product details");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReview = async (reviewId, userId) => {
    if (window.confirm("Are you sure you want to delete this review?")) {
      try {
        await reviewApi.deleteReview(reviewId, userId);
        await loadProductAndReviews();
      } catch (err) {
        setError(err.message || "Failed to delete review");
      }
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!product) return <div className="error">Product not found</div>;

  return (
    <div className="product-detail">
      <button className="back-btn" onClick={onBack}>
        ← Back to Products
      </button>

      <div className="product-header">
        <div className="product-info">
          <h1>{product.name}</h1>
          <p className="category">Category: {product.category}</p>
          <p className="description">{product.description}</p>
          <p className="price">Price: ₹{product.price.toFixed(2)}</p>
        </div>
        <div className="product-rating">
          <RatingDisplay
            rating={product.avg_rating}
            totalReviews={product.total_reviews}
            onRate={setInitialRating}
          />
        </div>
      </div>

      <ReviewForm
        productId={productId}
        initialRating={initialRating}
        onSuccess={() => {
          setInitialRating(0);
          loadProductAndReviews();
        }}
      />

      <div className="reviews-section">
        <h2>Reviews ({reviews.length})</h2>
        {reviews.length === 0 ? (
          <p className="no-reviews">No reviews yet. Be the first to review!</p>
        ) : (
          <div className="reviews-list">
            {reviews.map((review) => (
              <ReviewItem
                key={review._id}
                review={review}
                onDelete={(reviewId) => handleDeleteReview(reviewId, review.user_id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
