import React from 'react';
import { Product } from '../types';

interface ItemCardProps {
  item: Product;
  onAddToCart: (item: Product) => void;
}

const ItemCard: React.FC<ItemCardProps> = ({ item, onAddToCart }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden transition-transform duration-300 hover:scale-105 flex flex-col">
      <img src={item.imageUrl} alt={item.name} className="w-full h-28 object-cover"/>
      <div className="p-3 flex flex-col flex-grow">
        <h3 className="text-base font-semibold text-gray-800 mb-1">{item.name}</h3>
        <p className="text-sm text-gray-600 mb-2 flex-grow">{item.description}</p>
        <div className="flex justify-between items-center mt-auto">
          <p className="text-lg font-bold text-indigo-600">
            £{item.price.toFixed(2)}
          </p>
          <button
            onClick={() => onAddToCart(item)}
            className="bg-indigo-600 text-white font-semibold py-1.5 px-3 text-sm rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-300"
          >
            Add to Order
          </button>
        </div>
      </div>
    </div>
  );
};

export default ItemCard;
