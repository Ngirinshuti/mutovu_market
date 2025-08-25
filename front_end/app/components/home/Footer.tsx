export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-8">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <h3 className="font-bold mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="#" className="hover:text-white">About Us</a></li>
            <li><a href="#" className="hover:text-white">Careers</a></li>
            <li><a href="#" className="hover:text-white">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-3">Support</h3>
          <ul className="space-y-2">
            <li><a href="#" className="hover:text-white">Help Center</a></li>
            <li><a href="#" className="hover:text-white">Returns</a></li>
            <li><a href="#" className="hover:text-white">Shipping</a></li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-3">Legal</h3>
          <ul className="space-y-2">
            <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-white">Terms of Service</a></li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-3">Newsletter</h3>
          <input
            type="email"
            placeholder="Your email"
            className="px-4 py-2 rounded-lg w-full text-gray-900"
          />
          <button className="mt-3 bg-primary text-white px-4 py-2 rounded-lg w-full">
            Subscribe
          </button>
        </div>
      </div>
      <p className="text-center text-gray-500 mt-6">© 2025 Motuvu-market Store. All Rights Reserved.</p>
    </footer>
  );
}
