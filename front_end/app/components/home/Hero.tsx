"use client";
import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section className="relative bg-gradient-to-r from-white via-blue-100 to-gray-200 py-16">
      <div className="max-w-7xl mx-auto px-6">
        
        {/* Hero Grid Section */}
        <div className='hero-container flex flex-col-reverse md:grid md:grid-cols-3 md:gap-4 mb-8'>
          
          {/* Small Images Section */}
          <div className='small-images grid grid-cols-2 md:flex md:flex-col md:gap-1 md:col-span-1'>
            <motion.div 
              className='upper-image relative group cursor-pointer'
              initial={{ opacity: 0, x: -60 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              whileHover={{ scale: 1.02 }}
            >
              <img
                src='https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=600&h=300&fit=crop&crop=center'
                alt='Hot Phones'
                className='w-full h-[150px] md:h-[250px] object-cover rounded-lg'
              />
              <div className='absolute inset-0 bg-black bg-opacity-40 group-hover:bg-green-600 group-hover:bg-opacity-70 transition-all duration-300 flex items-center justify-center p-2 rounded-lg'>
                <p className='text-white text-lg md:text-xl font-bold text-center'>
                  Hot Deals from New Arrivals
                </p>
              </div>
            </motion.div>
            
            <motion.div 
              className='lower-image relative group cursor-pointer'
              initial={{ opacity: 0, x: -60 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              whileHover={{ scale: 1.02 }}
            >
              <img
                src='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&h=300&fit=crop&crop=center'
                alt='Best Shoes in Town'
                className='w-full h-[150px] md:h-[250px] object-cover rounded-lg'
              />
              <div className='absolute inset-0 bg-black bg-opacity-40 group-hover:bg-green-600 group-hover:bg-opacity-70 transition-all duration-300 flex items-center justify-center p-2 rounded-lg'>
                <p className='text-white text-lg md:text-xl font-bold text-center'>
                  Enjoy Black Friday Discount
                </p>
              </div>
            </motion.div>
          </div>
          
          {/* Large Hero Image */}
          <motion.div 
            className='large-image relative max-h-[250px] md:max-h-[500px] md:col-span-2'
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <img
              src="https://images.unsplash.com/photo-1619579719466-03d5847f92ba?q=80&w=1760&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
              alt="Step Into Style"
              className="w-full h-[250px] md:h-[500px] object-cover rounded-lg"
            />
            <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center rounded-lg">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="text-center space-y-4 px-4"
              >
                <h2 className="text-3xl md:text-5xl font-extrabold leading-tight text-white">
                  Step Into Style
                </h2>
                <p className="text-gray-200 text-lg hidden md:block">
                  Discover the latest trends in fashion, tech, and lifestyle.
                </p>
                <motion.button 
                  className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl font-semibold shadow-md transition-colors duration-200"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Shop Now
                </motion.button>
              </motion.div>
            </div>
          </motion.div>
          
        </div>
      </div>
    </section>
  );
}