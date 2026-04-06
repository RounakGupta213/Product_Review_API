import React, { useState } from "react";
import "./RatingDisplay.css";

export const RatingDisplay = ({ rating, totalReviews, onRate }) => {
  const [hoverRating, setHoverRating] = useState(0);
  const filledStars = Math.round(rating);

  return (
    <div className="rating-display">
      <div className="stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`star ${(hoverRating || filledStars) >= star ? "filled" : ""} ${
              onRate ? "interactive" : ""
            }`}
            onClick={(e) => {
              if (onRate) {
                e.stopPropagation();
                onRate(star);
              }
            }}
            onMouseEnter={() => onRate && setHoverRating(star)}
            onMouseLeave={() => onRate && setHoverRating(0)}
          >
            ★
          </span>
        ))}
      </div>
      <span className="rating-text">
        {rating.toFixed(1)} ({totalReviews} reviews)
      </span>
    </div>
  );
};
