"use client";
import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section className="relative bg-gradient-to-r from-green-200 via-blue-100 to-pink-200 py-16">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between px-6">
        <motion.div
          initial={{ opacity: 0, x: -80 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-4"
        >
          <h2 className="text-4xl md:text-5xl font-extrabold leading-tight">
            Step Into Style
          </h2>
          <p className="text-gray-600 text-lg">
            Discover the latest trends in fashion, tech, and lifestyle.
          </p>
          <button className="bg-primary text-white px-6 py-3 rounded-xl font-semibold shadow-md hover:opacity-90 transition">
            Shop Now
          </button>
        </motion.div>
        <motion.img
          src="https://images.unsplash.com/photo-1619579719466-03d5847f92ba?q=80&w=1760&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
          alt="Hero"
          className="w-full md:w-1/2 mt-8 md:mt-0"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
        />
      </div>
    </section>
  );
}
