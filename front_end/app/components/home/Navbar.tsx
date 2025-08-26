"use client";
import { motion } from "framer-motion";
import { Search, ShoppingCart, User, Menu } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const [searchFocus, setSearchFocus] = useState(false);

  return (
    <>
      {/* Main Navbar */}
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="sticky top-0 z-50 bg-white shadow-lg border-b border-gray-100"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          {/* Logo */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center space-x-2"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
              MUTOVU
            </h1>
          </motion.div>

          {/* Search Bar */}
          <div className="hidden md:flex flex-1 max-w-lg mx-8">
            <div className={`relative w-full transition-all duration-300 ${searchFocus ? 'transform scale-105' : ''}`}>
              <input
                type="text"
                placeholder="Search products..."
                onFocus={() => setSearchFocus(true)}
                onBlur={() => setSearchFocus(false)}
                className="w-full px-4 py-3 pr-12 rounded-full border-2 border-gray-200 focus:border-orange-400 focus:outline-none transition-all duration-300 bg-gray-50 focus:bg-white shadow-sm focus:shadow-md"
              />
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-orange-500 transition-colors duration-200"
              >
                <Search className="w-5 h-5" />
              </motion.button>
            </div>
          </div>

          {/* Right Icons */}
          <div className="flex items-center space-x-4">
            {/* Mobile Search */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="md:hidden p-2 text-gray-600 hover:text-orange-500 transition-colors duration-200"
            >
              <Search className="w-6 h-6" />
            </motion.button>

            {/* User Icon */}
            <motion.button
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 text-gray-600 hover:text-orange-500 transition-all duration-200 hover:bg-orange-50 rounded-full"
            >
              <User className="w-6 h-6" />
            </motion.button>

            {/* Cart Icon */}
            <motion.button
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="relative p-2 text-gray-600 hover:text-orange-500 transition-all duration-200 hover:bg-orange-50 rounded-full"
            >
              <ShoppingCart className="w-6 h-6" />
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-lg"
              >
                5
              </motion.span>
            </motion.button>

            {/* Mobile Menu */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="md:hidden p-2 text-gray-600 hover:text-orange-500 transition-colors duration-200"
            >
              <Menu className="w-6 h-6" />
            </motion.button>
          </div>
        </div>
      </motion.nav>

      {/* Category Navigation */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="bg-black text-white sticky top-[73px] z-40 shadow-lg"
      >
        <div className="max-w-7xl mx-auto">
          <div className="hidden md:flex items-center justify-center space-x-12 py-4">
            {['Plus', 'Flash sales', 'Babies', 'Fathers', 'Electronics', 'Fashion', 'Home & Garden', 'Sports'].map((category, index) => (
              <motion.a
                key={category}
                href="#"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -2 }}
                className="relative font-medium text-white hover:text-orange-400 transition-all duration-300 py-2 px-4 rounded-lg hover:bg-gray-800 group"
              >
                {category}
                <motion.div
                  className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-orange-400 to-red-400 group-hover:w-full transition-all duration-300"
                />
              </motion.a>
            ))}
          </div>
          
          {/* Mobile Category Menu */}
          <div className="md:hidden p-4">
            <select className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-600 focus:border-orange-400 focus:outline-none">
              <option>Choose Category</option>
              <option>Plus</option>
              <option>Flash sales</option>
              <option>Babies</option>
              <option>Fathers</option>
              <option>Electronics</option>
              <option>Fashion</option>
              <option>Home & Garden</option>
              <option>Sports</option>
            </select>
          </div>
        </div>
      </motion.div>
    </>
  );
}