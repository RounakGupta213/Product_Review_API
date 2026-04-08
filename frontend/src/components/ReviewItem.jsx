import React from "react";
import { RatingDisplay } from "./RatingDisplay";
import "./ReviewItem.css";

export const ReviewItem = ({ review, onDelete, currentUserId }) => {
  const isOwner = currentUserId === review.user_id;

  return (
    <div className="review-item">
      <div className="review-header">
        <div className="user-info">
          <strong>User: {review.username || "Anonymous"}</strong>
          <RatingDisplay rating={review.rating} totalReviews={1} />
        </div>
        {onDelete && isOwner && (
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
