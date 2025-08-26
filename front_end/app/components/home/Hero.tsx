"use client";
import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section className="relative bg-gradient-to-r from-white via-blue-100 to-gray-400 py-16">
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
              
                src='https://images.unsplash.com/photo-1583305727488-61f82c7eae4b?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
                alt='Hot Phones'
                className='w-full h-[400px] md:h-[250px] object-cover rounded-lg'
              />
              <div className='absolute inset-0 bg-opacity-40  group-hover:bg-opacity-70 transition-all duration-300 flex items-center justify-center p-2 rounded-lg'>
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
                src='https://images.unsplash.com/photo-1489269637500-aa0e75768394?q=80&w=1141&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
                alt='Best Shoes in Town'
                className='w-full h-[150px] md:h-[250px] object-cover rounded-lg'
              />
              <div className='absolute inset-0 bg-opacity-40 group-hover:bg-opacity-70 transition-all duration-300 flex items-center justify-center p-2 rounded-lg'>
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
              src="/assets/images/back.png"
              alt="Step Into Style"
              className="w-full h-[250px] md:h-[500px] object-cover rounded-lg"
            />
            <div className="absolute inset-0 bg-opacity-30 flex items-center justify-center rounded-lg">
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
                  className="bg-[#007A7A] hover:bg-green-700 text-white px-6 py-3 rounded-xl font-semibold shadow-md transition-colors duration-200"
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