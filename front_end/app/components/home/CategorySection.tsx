"use client";
import { motion } from "framer-motion";
import { categories } from "@/app/lib/data";

export default function CategorySection() {
  return (
    <section className="max-w-7xl mx-auto py-12 px-6">
      <h2 className="text-2xl font-bold mb-8">Shop By Category</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
        {categories.map((category, idx) => (
          <motion.div
            key={category.id}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-white shadow-md rounded-lg p-4 cursor-pointer hover:shadow-lg hover:-translate-y-1 transition"
          >
            <img src={category.icon} alt={category.name} className="w-12 mx-auto" />
            <p className="mt-2 text-center font-medium">{category.name}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
