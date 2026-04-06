import React, { useState, useEffect } from "react";
import { reviewApi } from "../services/api";
import { RatingInput } from "./RatingInput";
import "./ReviewForm.css";

export const ReviewForm = ({ productId, onSuccess, initialRating = 0 }) => {
  const [rating, setRating] = useState(initialRating);
  const [comment, setComment] = useState("");
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (initialRating > 0) {
      setRating(initialRating);
    }
  }, [initialRating]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!userId.trim()) {
      setError("Please enter your user ID");
      return;
    }

    if (rating === 0) {
      setError("Please select a rating");
      return;
    }

    if (comment.trim().length < 10) {
      setError("Comment must be at least 10 characters");
      return;
    }

    setLoading(true);

    try {
      await reviewApi.createReview(productId, {
        user_id: userId,
        rating,
        comment,
      });

      setRating(0);
      setComment("");
      setUserId("");
      onSuccess?.();
    } catch (err) {
      setError(err.message || "Failed to submit review");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="review-form">
      <h3>Write a Review</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Your User ID</label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter your user ID"
            required
          />
        </div>

        <div className="form-group">
          <RatingInput value={rating} onChange={setRating} />
        </div>

        <div className="form-group">
          <label>Your Review</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Write your review here (minimum 10 characters)"
            rows="5"
            required
          />
          <span className="char-count">
            {comment.length} / 5000 characters
          </span>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? "Submitting..." : "Submit Review"}
        </button>
      </form>
    </div>
  );
};
