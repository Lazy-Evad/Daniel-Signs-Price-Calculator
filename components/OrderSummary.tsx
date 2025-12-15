import React from 'react';
import { CartItem } from '../types';

interface OrderSummaryProps {
  cart: CartItem[];
  subtotal: number;
  vat: number;
  postage: number;
  grandTotal: number;
  userName: string;
  setUserName: (name: string) => void;
  purchaseOrder: string;
  setPurchaseOrder: (po: string) => void;
  updateQuantity: (id: number, quantity: number) => void;
  handleSubmitOrder: () => void;
  isSubmitting: boolean;
}

const PlusIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
    </svg>
);

const MinusIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
    </svg>
);

const TrashIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
);


const OrderSummary: React.FC<OrderSummaryProps> = ({
    cart,
    subtotal,
    vat,
    postage,
    grandTotal,
    userName,
    setUserName,
    purchaseOrder,
    setPurchaseOrder,
    updateQuantity,
    handleSubmitOrder,
    isSubmitting
}) => {
    const isSubmitDisabled = cart.length === 0 || !purchaseOrder.trim() || !userName.trim() || isSubmitting;

    return (
        <div className="lg:sticky lg:top-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-800 border-b pb-4 mb-4">Your Order</h2>
                {cart.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">Your order is empty.</p>
                ) : (
                    <>
                        <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                            {cart.map(item => (
                                <div key={item.id} className="flex justify-between items-start py-2 border-b last:border-b-0">
                                    <div className="flex-grow">
                                        <p className="font-semibold text-gray-700">{item.name}</p>
                                        <div className="flex items-center mt-1">
                                            <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="p-1 rounded-full text-gray-500 hover:bg-gray-200"><MinusIcon/></button>
                                            <span className="w-8 text-center font-medium text-gray-800">{item.quantity}</span>
                                            <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="p-1 rounded-full text-gray-500 hover:bg-gray-200"><PlusIcon/></button>
                                            <button onClick={() => updateQuantity(item.id, 0)} className="text-red-500 hover:text-red-700 ml-3 p-1"><TrashIcon/></button>
                                        </div>
                                    </div>
                                    <div className="text-right ml-4 flex-shrink-0">
                                        <p className="font-semibold text-gray-800">£{(item.price * item.quantity).toFixed(2)}</p>
                                        <p className="text-sm text-gray-500">@ £{item.price.toFixed(2)}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="border-t pt-4 mt-4 space-y-2 text-sm text-gray-600">
                            <p className="italic text-center text-gray-500 mb-2">All prices are exclusive of VAT.</p>
                            <div className="flex justify-between">
                                <span>Subtotal</span>
                                <span>£{subtotal.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Postage</span>
                                <span>£{postage.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>VAT (20%)</span>
                                <span>£{vat.toFixed(2)}</span>
                            </div>
                        </div>
                    </>
                )}
                <div className="border-t pt-4 mt-4 space-y-4">
                     <div className="bg-indigo-50 rounded-lg p-4">
                        <div className="flex justify-between items-center font-bold text-2xl text-indigo-800">
                            <span>Total to Raise P/O:</span>
                            <span>£{grandTotal.toFixed(2)}</span>
                        </div>
                    </div>
                     <div>
                        <label htmlFor="user-name" className="block text-sm font-medium text-gray-700 mb-1">
                            Your Name <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            id="user-name"
                            value={userName}
                            onChange={(e) => setUserName(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="Enter your name"
                        />
                    </div>
                    <div>
                        <label htmlFor="po-number" className="block text-sm font-medium text-gray-700 mb-1">
                            Purchase Order Number <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            id="po-number"
                            value={purchaseOrder}
                            onChange={(e) => setPurchaseOrder(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="Enter PO Number"
                        />
                    </div>
                    <button
                        onClick={handleSubmitOrder}
                        disabled={isSubmitDisabled}
                        className="w-full bg-green-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                        {isSubmitting ? (
                            <>
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Submitting...
                            </>
                        ) : (
                            'Submit Order'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default OrderSummary;