"use client";
import { motion } from "framer-motion";
import { Search } from "lucide-react";

export default function Navbar() {
  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="sticky top-0 z-50 bg-white shadow-md"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        <h1 className="text-2xl font-bold text-primary">Mutovu Logo</h1>
        <div className="hidden md:flex space-x-6 font-medium">
          <a href="#" className="hover:text-primary transition">Home</a>
          <a href="#" className="hover:text-primary transition">Shop</a>
          <a href="#" className="hover:text-primary transition">About</a>
          <a href="#" className="hover:text-primary transition">Contact</a>
        </div>
        <Search className="w-6 h-6 cursor-pointer hover:text-primary transition" />
      </div>
    </motion.nav>
  );
}
