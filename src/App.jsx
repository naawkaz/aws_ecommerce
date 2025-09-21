import React, { useState, useRef, useCallback } from 'react';
import { useDropzone } from "react-dropzone";
import Cropper from "react-easy-crop";

// Custom Icons (no external dependencies needed)
function CameraIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  );
}

function UserIcon() {
  return (
    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  );
}

function CartIcon() {
  return (
    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.1 5M7 13l-1.1 5m0 0h9.2M17 18a2 2 0 11-4 0 2 2 0 014 0zM9 18a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  );
}

function ArrowLeftIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  );
}

function MinusIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
    </svg>
  );
}

// Sample data
const getSampleProducts = () => [
  {
    id: 1,
    name: "New Balance Shoes Air Force",
    category: "Footwear",
    brand: "New Balance",
    price: 49.00,
    rating: 4.5,
    description: "High-quality athletic shoes designed for comfort and performance. Perfect for daily workouts and casual wear with advanced cushioning technology.",
    imageUrl: "https://m.media-amazon.com/images/I/61WpUk8IiXL._AC_SX679_.jpg"
  },
  {
    id: 2,
    name: "Red Raincoat Waterproof",
    category: "Outerwear",
    brand: "WeatherShield",
    price: 99.00,
    rating: 4.7,
    description: "Premium waterproof raincoat with breathable fabric. Keeps you dry in the heaviest downpours while maintaining comfort.",
    imageUrl: "https://m.media-amazon.com/images/I/61WpUk8IiXL._AC_SX679_.jpg"
  },
  {
    id: 3,
    name: "Wireless Headphones Pro",
    category: "Electronics",
    brand: "SoundMax",
    price: 159.00,
    rating: 4.8,
    description: "Premium wireless headphones with noise cancellation and 30-hour battery life. Perfect for music lovers and professionals.",
    imageUrl: "https://m.media-amazon.com/images/I/61WpUk8IiXL._AC_SX679_.jpg"
  },
  {
    id: 4,
    name: "Smart Watch Series 5",
    category: "Electronics",
    brand: "TechWear",
    price: 299.00,
    rating: 4.6,
    description: "Advanced smartwatch with health monitoring, GPS, and 7-day battery life. Track your fitness and stay connected.",
    imageUrl: "https://m.media-amazon.com/images/I/61WpUk8IiXL._AC_SX679_.jpg"
  },
  {
    id: 5,
    name: "Leather Backpack",
    category: "Accessories",
    brand: "UrbanStyle",
    price: 129.00,
    rating: 4.4,
    description: "Premium leather backpack with laptop compartment and multiple pockets for organization. Perfect for work and travel.",
    imageUrl: "https://m.media-amazon.com/images/I/61WpUk8IiXL._AC_SX679_.jpg"
  },
  {
    id: 6,
    name: "Running Jacket",
    category: "Sportswear",
    brand: "ActiveFit",
    price: 79.00,
    rating: 4.3,
    description: "Lightweight running jacket with moisture-wicking fabric and reflective details. Ideal for outdoor workouts in any weather.",
    imageUrl: "https://m.media-amazon.com/images/I/61WpUk8IiXL._AC_SX679_.jpg"
  }
];

// Utility functions
const formatPrice = (price) => `RM ${price.toFixed(0)}`;

const showNotification = (message) => {
  alert(message); // In real app, use toast library
};

// Utility function to create cropped image
const createImage = (url) =>
  new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener('load', () => resolve(image));
    image.addEventListener('error', (error) => reject(error));
    image.setAttribute('crossOrigin', 'anonymous');
    image.src = url;
  });

const getCroppedImg = async (imageSrc, pixelCrop) => {
  const image = await createImage(imageSrc);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  canvas.width = pixelCrop.width;
  canvas.height = pixelCrop.height;

  ctx.drawImage(
    image,
    pixelCrop.x,
    pixelCrop.y,
    pixelCrop.width,
    pixelCrop.height,
    0,
    0,
    pixelCrop.width,
    pixelCrop.height
  );

  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve(blob);
    }, 'image/jpeg', 0.9);
  });
};

// Prominent Search Section Component
function ProminentSearchSection({ searchQuery, onSearchChange, onSearch, onImageSearch }) {
  const [showImageUpload, setShowImageUpload] = useState(false);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  const handleImageSelect = (file) => {
    onImageSearch(file);
    setShowImageUpload(false);
  };

  return (
    <div className="max-w-4xl mx-auto mb-12">
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">Find what you're looking for</h2>
          <p className="text-gray-600">Upload an image to discover similar products</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search for products, brands, categories..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full px-6 py-4 text-lg border border-gray-300 rounded-2xl focus:outline-none focus:ring-3 focus:ring-blue-500 focus:border-transparent shadow-sm"
            />
          </div>
          <button
            onClick={() => setShowImageUpload(!showImageUpload)}
            className="p-4 bg-gray-100 hover:bg-gray-200 rounded-2xl transition-colors shadow-sm group"
            title="Search by image"
          >
            <CameraIcon />
          </button>
          <button
            onClick={onSearch}
            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl transition-colors font-semibold shadow-sm hover:shadow-md transform hover:scale-105"
          >
            Search
          </button>
        </div>

      </div>

      {/* Image Upload Modal */}
      <ImageUploadModal
        isOpen={showImageUpload}
        onClose={() => setShowImageUpload(false)}
        onImageSelect={handleImageSelect}
      />
    </div>
  );
}

// Simplified Header for Discovery Page
function DiscoveryHeader() {
  return (
    <div className="bg-white shadow-sm border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="text-2xl">🔺</div>
            <span className="text-xl font-bold text-gray-900">Serverless and senseless</span>
          </div>

          {/* Right Icons */}
          <div className="flex items-center space-x-3">
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <UserIcon />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <CartIcon />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}



// Image Preview Modal Component
function ImagePreviewModal({ isOpen, imageFile, onClose }) {
  if (!isOpen || !imageFile) return null;

  const imageUrl = imageFile instanceof File ? URL.createObjectURL(imageFile) : imageFile;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="max-w-4xl max-h-[90vh] mx-4">
        <div className="bg-white rounded-lg overflow-hidden">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="text-lg font-semibold">Search Image Preview</h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-xl font-bold"
            >
              ×
            </button>
          </div>
          <div className="p-4">
            <img
              src={imageUrl}
              alt="Search preview"
              className="max-w-full max-h-[70vh] object-contain mx-auto"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Search Image Display Component
// Search Image Display Component
function SearchImageDisplay({ imageFile, onImageClick, predictedCategory }) {
  if (!imageFile) return null;

  const imageUrl = imageFile instanceof File ? URL.createObjectURL(imageFile) : imageFile;

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-4 relative">
      {/* AI Detected Category - Top Right */}
      {predictedCategory && (
        <div className="absolute top-4 right-4">
          <p className="text-xl text-blue-500 font-medium bg-blue-50 px-3 py-1 rounded-full border border-green-200">
            🔎 Detected sub-category: {predictedCategory}
          </p>
        </div>
      )}

      <div className="flex items-center space-x-4">
        <div className="flex-shrink-0">
          <img
            src={imageUrl}
            alt="Search image"
            className="w-20 h-20 object-cover rounded-lg cursor-pointer hover:opacity-80 transition-opacity"
            onClick={onImageClick}
          />
        </div>
        <div className="flex-1 pr-32">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="font-medium text-gray-900">Searching with this image</h3>
          </div>
          <p className="text-xs text-gray-400 mt-1">Click image to view full size</p>
        </div>
      </div>
    </div>
  );
}

// Improved Image Upload Modal Component
function ImageUploadModal({ isOpen, onClose, onImageSelect }) {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [showCropper, setShowCropper] = useState(false);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setUploadedImage(reader.result);
        setShowCropper(true);
        // Reset crop state when new image is loaded
        setCrop({ x: 0, y: 0 });
        setZoom(1);
      };
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    maxFiles: 1
  });

  const onCropComplete = useCallback((croppedArea, croppedAreaPixels) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const handleCropConfirm = async () => {
    try {
      const croppedImageBlob = await getCroppedImg(uploadedImage, croppedAreaPixels);

      // Create a File object from the blob
      const croppedFile = new File([croppedImageBlob], "cropped-image.jpg", {
        type: "image/jpeg"
      });

      onImageSelect(croppedFile);
      handleClose();
    } catch (error) {
      console.error('Error cropping image:', error);
    }
  };

  const handleClose = () => {
    setUploadedImage(null);
    setShowCropper(false);
    setCrop({ x: 0, y: 0 });
    setZoom(1);
    setCroppedAreaPixels(null);
    onClose();
  };

  const handleCancel = () => {
    setShowCropper(false);
    setUploadedImage(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">Search by Image</h3>
        </div>

        <div className="p-4">
          {!showCropper ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
                }`}
            >
              <input {...getInputProps()} />
              <div className="flex flex-col items-center space-y-2">
                <CameraIcon />
                <p className="text-gray-600">
                  {isDragActive ? "Drop the image here..." : "Drag & drop an image here, or click to choose"}
                </p>
                <p className="text-sm text-gray-400">
                  Supports: JPG, PNG, GIF, WebP
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative h-64 bg-gray-100 rounded-lg overflow-hidden">
                <Cropper
                  image={uploadedImage}
                  crop={crop}
                  zoom={zoom}
                  aspect={1}
                  onCropChange={setCrop}
                  onZoomChange={setZoom}
                  onCropComplete={onCropComplete}
                />
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Zoom: {Math.round(zoom * 100)}%
                  </label>
                  <input
                    type="range"
                    min={1}
                    max={3}
                    step={0.1}
                    value={zoom}
                    onChange={(e) => setZoom(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={handleCropConfirm}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    Use Cropped Image
                  </button>
                  <button
                    onClick={handleCancel}
                    className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t bg-gray-50 flex justify-end">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// Header Component
function Header({ searchQuery, onSearchChange, onSearch, onImageSearch }) {
  const [showImageUpload, setShowImageUpload] = useState(false);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  const handleImageSelect = (file) => {
    onImageSearch(file);
    setShowImageUpload(false);
  };

  return (
    <div className="bg-white shadow-sm border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="text-2xl">🔺</div>
            <span className="text-xl font-bold text-gray-900">Serverless and senseless</span>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl mx-8">
            <div className="flex items-center space-x-2">
              <div className="flex-1 relative">
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => onSearchChange(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button
                onClick={() => setShowImageUpload(!showImageUpload)}
                className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              >
                <CameraIcon />
              </button>
              <button
                onClick={onSearch}
                className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors"
              >
                <SearchIcon />
              </button>
            </div>
          </div>

          {/* Right Icons */}
          <div className="flex items-center space-x-3">
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <UserIcon />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <CartIcon />
            </button>
          </div>
        </div>

        {/* Image Upload Modal */}
        <ImageUploadModal
          isOpen={showImageUpload}
          onClose={() => setShowImageUpload(false)}
          onImageSelect={handleImageSelect}
        />
      </div>
    </div>
  );
};

// Product Image Component
const ProductImage = ({ productName, imageUrl, isLarge }) => {
  return (
    <div
      className={`bg-gray-100 flex items-center justify-center ${isLarge ? "h-80" : "h-48"
        }`}
    >
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={productName}
          className="object-contain h-full w-full"
        />
      ) : (
        <span className="text-4xl">📦</span>
      )}
    </div>
  );
};

// Product Card Component
function ProductCard({ product, onProductClick, onAddToCart }) {
  const handleCardClick = () => {
    onProductClick(product);
  };

  const handleAddToCart = (e) => {
    e.stopPropagation();
    onAddToCart(product);
  };

  return (
    <div
      className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1 border border-gray-100"
      onClick={handleCardClick}
    >
      <div className="aspect-w-16 aspect-h-12 bg-gradient-to-br from-gray-100 to-gray-200 rounded-t-xl flex items-center justify-center">
        <ProductImage productName={product.name} imageUrl={product.imageUrl} />
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 text-lg mb-1">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-2">({product.category}) - {product.brand}</p>
        <div className="flex items-center justify-between mb-3">
          <span className="text-2xl font-bold text-green-600">{formatPrice(product.price)}</span>
          <span className="text-sm text-gray-500">{product.rating} Rating</span>
        </div>
        <button
          onClick={handleAddToCart}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors font-medium"
        >
          Add to Cart
        </button>
      </div>
    </div>
  );
}

// Quantity Selector Component
function QuantitySelector({ quantity, onQuantityChange }) {
  const decrease = () => {
    if (quantity > 1) {
      onQuantityChange(quantity - 1);
    }
  };

  const increase = () => {
    onQuantityChange(quantity + 1);
  };

  return (
    <div className="flex items-center space-x-3">
      <button
        onClick={decrease}
        className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        disabled={quantity <= 1}
      >
        <MinusIcon />
      </button>
      <span className="text-xl font-semibold px-4">{quantity}</span>
      <button
        onClick={increase}
        className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <PlusIcon />
      </button>
    </div>
  );
}

// Horizontal Filter Bar Component
// Horizontal Filter Bar Component
// Horizontal Filter Bar Component
function FilterBar() {
  return (
    <div className="bg-white rounded-lg shadow-sm px-6 py-3 mb-6 border border-gray-200">
      <div className="flex items-center justify-between gap-6">
        <div className="flex items-center gap-1">
          <h3 className="text-sm font-semibold text-gray-900">Refine AI Search</h3>
          <span className="text-xs text-gray-500">• Filters help AI find more precise matches</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-xs font-medium text-gray-700">Category</label>
            <select className="border border-gray-300 rounded-full px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white">
              <option>All Categories</option>
              {/* <option>Footwear</option>
              <option>Outerwear</option>
              <option>Electronics</option>
              <option>Accessories</option>
              <option>Sportswear</option> */}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs font-medium text-gray-700">Brand</label>
            <select className="border border-gray-300 rounded-full px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white">
              <option>All Brands</option>
              {/* <option>New Balance</option>
              <option>WeatherShield</option>
              <option>SoundMax</option>
              <option>TechWear</option> */}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs font-medium text-gray-700">Price</label>
            <div className="flex gap-1">
              <input
                type="number"
                placeholder="Min"
                className="w-16 border border-gray-300 rounded-full px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <input
                type="number"
                placeholder="Max"
                className="w-16 border border-gray-300 rounded-full px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <button className="px-4 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors text-sm font-medium">
            Filter
          </button>
        </div>
      </div>
    </div>
  );
}

// Product Grid Component
function ProductGrid({ products, onProductClick, onAddToCart, columns = 4 }) {
  const gridClass = {
    3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
  }[columns] || "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4";

  return (
    <div className={`grid ${gridClass} gap-6`}>
      {products.map((product, index) => (
        <ProductCard
          key={`${product.id}-${index}`}
          product={product}
          onProductClick={onProductClick}
          onAddToCart={onAddToCart}
        />
      ))}
    </div>
  );
}

// Page Components
function DiscoveryPage({ searchQuery, onSearchChange, onSearch, onImageSearch, onProductClick, onAddToCart }) {
  const products = getSampleProducts();

  return (
    <div className="min-h-screen bg-gray-50">
      <DiscoveryHeader />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Prominent Search Section */}
        <ProminentSearchSection
          searchQuery={searchQuery}
          onSearchChange={onSearchChange}
          onSearch={onSearch}
          onImageSearch={onImageSearch}
        />

        <h1 className="text-4xl font-bold text-center text-gray-900 mb-8">Discover</h1>
        <ProductGrid
          products={products}
          onProductClick={onProductClick}
          onAddToCart={onAddToCart}
          columns={4}
        />
      </div>
    </div>
  );
}

function ResultsPage({ searchQuery, onSearchChange, onSearch, onImageSearch, onProductClick, onAddToCart, onBack, searchImage, predictedCategory }) {
  const [showImagePreview, setShowImagePreview] = useState(false);
  const products = getSampleProducts();
  const duplicatedProducts = [...products, ...products];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        onSearch={onSearch}
        onImageSearch={onImageSearch}
      />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-start mb-6">
          <button
            onClick={onBack}
            className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors cursor-pointer"
          >
            <ArrowLeftIcon />
            <span>Back to Discovery</span>
          </button>
        </div>

        {/* Search Image Display */}
        <SearchImageDisplay
          imageFile={searchImage}
          onImageClick={() => setShowImagePreview(true)}
          predictedCategory={predictedCategory}
        />

        {/* Horizontal Filter Bar */}
        <FilterBar />

        {/* Results Heading - Now below filter bar */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Results</h1>
          <span className="text-gray-600">Showing {duplicatedProducts.length} Products</span>
        </div>

        {/* Centered Product Grid */}
        <div className="flex justify-center">
          <div className="max-w-6xl w-full">
            <ProductGrid
              products={duplicatedProducts}
              onProductClick={onProductClick}
              onAddToCart={onAddToCart}
              columns={4}
            />
          </div>
        </div>

        {/* Image Preview Modal */}
        <ImagePreviewModal
          isOpen={showImagePreview}
          imageFile={searchImage}
          onClose={() => setShowImagePreview(false)}
        />
      </div>
    </div>
  );
}

function ProductDetailPage({ searchQuery, onSearchChange, onSearch, onImageSearch, selectedProduct, onBack, onAddToCart }) {
  const [quantity, setQuantity] = useState(1);

  if (!selectedProduct) return null;

  const handleAddToCart = () => {
    onAddToCart(selectedProduct, quantity);
  };

  const totalPrice = selectedProduct.price * quantity;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        onSearch={onSearch}
        onImageSearch={onImageSearch}
      />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6 transition-colors cursor-pointer"
        >
          <ArrowLeftIcon />
          <span>Back to Discovery</span>
        </button>

        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Product Images */}
            <div className="p-8">
              <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex items-center justify-center mb-4">
                <ProductImage
                  productName={selectedProduct.name}
                  isLarge
                  imageUrl={selectedProduct.imageUrl}
                />
              </div>
              <div className="grid grid-cols-4 gap-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors">
                    <span className="text-xs text-gray-400">Image {i}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Product Info */}
            <div className="p-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{selectedProduct.name}</h1>
              <div className="space-y-2 mb-6">
                <p className="text-gray-600">Category: {selectedProduct.category}</p>
                <p className="text-gray-600">Brand: {selectedProduct.brand}</p>
                <p className="text-gray-600">{selectedProduct.rating} Rating</p>
              </div>

              <div className="text-4xl font-bold text-green-600 mb-6">
                {formatPrice(selectedProduct.price)}
              </div>

              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-700 leading-relaxed">{selectedProduct.description}</p>
              </div>

              {/* Quantity Selector */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Quantity</h3>
                <QuantitySelector quantity={quantity} onQuantityChange={setQuantity} />
              </div>

              {/* Shipping Info */}
              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">🚚 Shipping</h3>
                <p className="text-gray-700">Shipping information available at checkout</p>
              </div>

              {/* Add to Cart Button */}
              <button
                onClick={handleAddToCart}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-4 px-8 rounded-xl font-semibold text-lg transition-all transform hover:scale-[1.02] shadow-lg"
              >
                Add to Cart - {formatPrice(totalPrice)}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  const [currentPage, setCurrentPage] = useState('discovery');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchImage, setSearchImage] = useState(null);
  const [predictedCategory, setPredictedCategory] = useState(null);

  // Navigation functions
  const navigateToResults = () => setCurrentPage('results');
  const navigateToProduct = (product) => {
    setSelectedProduct(product);
    setCurrentPage('product');
  };

  const navigateToDiscovery = () => {
    setCurrentPage('discovery');
    // Clear search states when going back to discovery
    setPredictedCategory(null);
    setSearchImage(null);
  };

  // Search functions
  const handleSearch = () => {
    if (searchQuery.trim()) {
      navigateToResults();
    } else {
      showNotification('Please enter a search term or upload an image');
    }
  };

  const handleImageSearch = (file) => {
    setSearchImage(file);

    // Simulate AWS Lambda prediction (replace with actual API call later)
    setPredictedCategory('Sandals');

    showNotification(`Searching with image: ${file.name} (${Math.round(file.size / 1024)}KB)`);
    navigateToResults();
  };

  // Cart function
  const handleAddToCart = (product, qty = 1) => {
    showNotification(`Added ${qty} × ${product.name} to cart!`);
  };

  // Common props for all pages
  const commonProps = {
    searchQuery,
    onSearchChange: setSearchQuery,
    onSearch: handleSearch,
    onImageSearch: handleImageSearch,
    onProductClick: navigateToProduct,
    onAddToCart: handleAddToCart
  };

  // Page routing
  switch (currentPage) {
    case 'results':
      return <ResultsPage
        {...commonProps}
        onBack={navigateToDiscovery}
        searchImage={searchImage}
        predictedCategory={predictedCategory}
      />;
    case 'product':
      return (
        <ProductDetailPage
          {...commonProps}
          selectedProduct={selectedProduct}
          onBack={navigateToDiscovery}
        />
      );
    default:
      return <DiscoveryPage {...commonProps} />;
  }
};

export default App;