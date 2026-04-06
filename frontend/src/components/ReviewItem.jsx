import React from "react";
import { RatingDisplay } from "./RatingDisplay";
import "./ReviewItem.css";

export const ReviewItem = ({ review, onDelete }) => {
  return (
    <div className="review-item">
      <div className="review-header">
        <div className="user-info">
          <strong>User ID: {review.user_id}</strong>
          <RatingDisplay rating={review.rating} totalReviews={1} />
        </div>
        {onDelete && (
          <button className="delete-btn" onClick={() => onDelete(review._id)}>
            Delete
          </button>
        )}
      </div>
      <p className="review-comment">{review.comment}</p>
      <span className="review-date">
        {new Date(review.created_at).toLocaleDateString()}
      </span>
    </div>
  );
};
