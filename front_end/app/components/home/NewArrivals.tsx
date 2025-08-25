"use client";
import ProductCard from "./ProductCard";
import { products } from "@/app/lib/data";

export default function NewArrivals() {
  return (
    <section className="max-w-7xl mx-auto py-12 px-6">
      <h2 className="text-2xl font-bold mb-8">New Arrivals</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {products.slice(0, 4).map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
