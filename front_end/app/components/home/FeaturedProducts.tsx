"use client";
import ProductCard from "./ProductCard";
import { products } from "@/app/lib/data";

export default function FeaturedProducts() {
  return (
    <section className="max-w-7xl mx-auto py-12 px-6">
      <h2 className="text-2xl font-bold mb-8">Featured Products</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {products.slice(4, 8).map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
