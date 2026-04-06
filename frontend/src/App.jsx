import React, { useState } from "react";
import { ProductList } from "./pages/ProductList";
import { ProductDetail } from "./pages/ProductDetail";
import "./App.css";

function App() {
  const [selectedProductId, setSelectedProductId] = useState(null);

  return (
    <div className="App">
      <header className="app-header">
        <h1>Product Review System</h1>
      </header>

      <main>
        {selectedProductId ? (
          <ProductDetail
            productId={selectedProductId}
            onBack={() => setSelectedProductId(null)}
          />
        ) : (
          <ProductList onSelectProduct={setSelectedProductId} />
        )}
      </main>
    </div>
  );
}

export default App;