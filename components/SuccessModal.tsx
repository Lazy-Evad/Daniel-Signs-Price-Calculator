import React, { Fragment } from 'react';

interface SuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  userName: string;
  purchaseOrder: string;
  grandTotal: number;
}

const SuccessModal: React.FC<SuccessModalProps> = ({ isOpen, onClose, userName, purchaseOrder, grandTotal }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
          <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>
        <h3 className="text-2xl font-bold text-gray-900">Order Submitted!</h3>
        <div className="mt-2 px-7 py-3">
          <p className="text-gray-600">
            Your order has been successfully submitted. We will process it shortly.
          </p>
        </div>
        <div className="mt-4 bg-gray-50 rounded-lg p-4 text-left">
            <h4 className="font-semibold text-lg text-gray-800 mb-2">Order Summary</h4>
            <div className="space-y-1 text-gray-700">
                <div className="flex justify-between">
                    <span>Name:</span>
                    <span className="font-medium">{userName}</span>
                </div>
                <div className="flex justify-between">
                    <span>PO Number:</span>
                    <span className="font-mono font-medium">{purchaseOrder}</span>
                </div>
                <div className="flex justify-between font-bold">
                    <span>Grand Total:</span>
                    <span>£{grandTotal.toFixed(2)}</span>
                </div>
            </div>
        </div>
        <div className="mt-6">
          <button
            onClick={onClose}
            type="button"
            className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
          >
            Create New Order
          </button>
        </div>
      </div>
    </div>
  );
};

export default SuccessModal;