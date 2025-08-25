"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingCart } from "lucide-react";
import { Product } from "@/app/types";

type Props = {
  product: Product;
  onAddToCart?: (product: Product) => void | Promise<void>;
};

export default function ProductCard({ product, onAddToCart }: Props) {
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

  const handleAdd = async () => {
    if (adding) return;
    setAdding(true);
    try {
      await Promise.resolve(onAddToCart?.(product));
      setAdded(true);
      setTimeout(() => setAdded(false), 1200);
    } finally {
      setAdding(false);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="group bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition"
    >
      <div className="relative">
        <img
          src={product.image}
          alt={product.name}
          className="rounded-lg h-48 w-full object-cover"
        />

        {/* little 'Added!' chip */}
        <AnimatePresence>
          {added && (
            <motion.span
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-3 right-3 rounded-full bg-green-600 text-white text-xs font-medium px-3 py-1 shadow"
            >
              Added!
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-3">
        <h3 className="font-semibold text-lg">{product.name}</h3>
        <p className="text-gray-500 text-sm">{product.brand}</p>
        <div className="mt-3 flex items-center justify-between">
          <p className="font-bold text-primary">${product.price}</p>

          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleAdd}
            disabled={adding}
            aria-label={`Add ${product.name} to cart`}
            className="inline-flex items-center gap-2 rounded-lg bg-primary text-green-400 px-4 py-2 font-medium shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <ShoppingCart className="h-4 w-4 text-red-600" />
            {adding ? "Adding..." : "Add to Cart"}
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
