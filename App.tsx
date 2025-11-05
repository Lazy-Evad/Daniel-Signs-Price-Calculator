import React, { useState, useMemo, useCallback } from 'react';
import { PREDETERMINED_ITEMS } from './constants';
import { Product, CartItem } from './types';
import Header from './components/Header';
import ItemCard from './components/ItemCard';
import OrderSummary from './components/OrderSummary';
import SuccessModal from './components/SuccessModal';

const VAT_RATE = 0.20;
const POSTAGE_COST = 8.00;

function App() {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [purchaseOrder, setPurchaseOrder] = useState('');
  const [userName, setUserName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [submittedPO, setSubmittedPO] = useState('');
  const [submittedUserName, setSubmittedUserName] = useState('');
  const [submittedTotal, setSubmittedTotal] = useState(0);

  const subtotal = useMemo(() => {
    return cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
  }, [cart]);

  const vat = useMemo(() => {
    return subtotal * VAT_RATE;
  }, [subtotal]);

  const postage = useMemo(() => {
    return cart.length > 0 ? POSTAGE_COST : 0;
  }, [cart]);

  const grandTotal = useMemo(() => {
    return subtotal + vat + postage;
  }, [subtotal, vat, postage]);

  const handleAddToCart = useCallback((product: Product) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.id === product.id);
      if (existingItem) {
        return prevCart.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prevCart, { ...product, quantity: 1 }];
    });
  }, []);

  const updateQuantity = useCallback((productId: number, newQuantity: number) => {
    setCart((prevCart) => {
      if (newQuantity <= 0) {
        return prevCart.filter((item) => item.id !== productId);
      }
      return prevCart.map((item) =>
        item.id === productId ? { ...item, quantity: newQuantity } : item
      );
    });
  }, []);

  const handleSubmitOrder = () => {
    if (cart.length === 0 || !purchaseOrder.trim() || !userName.trim()) return;

    setIsSubmitting(true);
    setSubmittedPO(purchaseOrder);
    setSubmittedUserName(userName);
    setSubmittedTotal(grandTotal);
    
    // Simulate API call to send email or create Trello card
    console.log('Submitting Order:', {
      userName,
      purchaseOrder,
      items: cart,
      subtotal: subtotal,
      postage: postage,
      vat: vat,
      total: grandTotal,
    });
    setTimeout(() => {
      setIsSubmitting(false);
      setShowSuccessModal(true);
      setCart([]);
      setPurchaseOrder('');
      setUserName('');
    }, 2000); // 2-second delay to simulate network request
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <Header />
      <main className="container mx-auto p-4 lg:p-8">
        <div className="lg:grid lg:grid-cols-3 lg:gap-8">
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Select Items</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {PREDETERMINED_ITEMS.map((item) => (
                <ItemCard key={item.id} item={item} onAddToCart={handleAddToCart} />
              ))}
            </div>
          </div>
          <div className="mt-8 lg:mt-0 lg:col-span-1">
             <OrderSummary
                cart={cart}
                subtotal={subtotal}
                vat={vat}
                postage={postage}
                grandTotal={grandTotal}
                userName={userName}
                setUserName={setUserName}
                purchaseOrder={purchaseOrder}
                setPurchaseOrder={setPurchaseOrder}
                updateQuantity={updateQuantity}
                handleSubmitOrder={handleSubmitOrder}
                isSubmitting={isSubmitting}
            />
          </div>
        </div>
      </main>
      <SuccessModal 
        isOpen={showSuccessModal} 
        onClose={() => setShowSuccessModal(false)}
        userName={submittedUserName}
        purchaseOrder={submittedPO}
        grandTotal={submittedTotal}
      />
    </div>
  );
}

export default App;