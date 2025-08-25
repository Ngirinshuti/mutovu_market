import CategorySection from "./components/home/CategorySection";
import FeaturedProducts from "./components/home/FeaturedProducts";
import Footer from "./components/home/Footer";
import Hero from "./components/home/Hero";
import Navbar from "./components/home/Navbar";
import NewArrivals from "./components/home/NewArrivals";

export default function Home() {
  return (
    <>
      <Navbar />
      <Hero />
      <CategorySection />
      <NewArrivals />
      <FeaturedProducts />
      <Footer />
    </>
  );
}
