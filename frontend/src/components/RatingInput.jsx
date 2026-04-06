import React, { useState } from "react";
import "./RatingInput.css";

export const RatingInput = ({ value, onChange }) => {
  const [hoverRating, setHoverRating] = useState(0);

  return (
    <div className="rating-input">
      <label>Rating (1-5 stars) - Click to rate</label>
      <div className="star-container">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            className={`star ${(hoverRating || value) >= star ? "active" : ""}`}
            onClick={() => onChange(star)}
            onMouseEnter={() => setHoverRating(star)}
            onMouseLeave={() => setHoverRating(0)}
            type="button"
          >
            ★
          </button>
        ))}
      </div>
      <span className="rating-value">{value > 0 ? `${value}/5` : "Click stars to rate"}</span>
    </div>
  );
};
