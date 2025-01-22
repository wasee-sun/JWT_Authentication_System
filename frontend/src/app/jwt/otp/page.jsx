'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { verifyOtpAction, resendOtpAction } from '@/actions/authActions';
import { OtpVerifyButton, ResendOtpButton } from '@/components/Buttons/Button';
import { BASE_ROUTE, DEFAULT_LOGIN_REDIRECT } from '@/route';
import { decrypt } from '@/libs/session';
import styles from './page.module.css';

export default function OtpPage() {
  const router = useRouter();
  const [timer, setTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const intervalRef = useRef(null);

  useEffect(() => {
    const otpRequired = sessionStorage.getItem('otpRequired');
    const otpExpiry = sessionStorage.getItem('otpExpiry');

    if (!otpRequired || Date.now() > parseInt(otpExpiry, 10)) {
      router.push(`${BASE_ROUTE}/login`);
    }

    // Start the timer when the component is mounted
    intervalRef.current = setInterval(() => {
      setTimer((prevTimer) => {
        if (prevTimer === 0) {
          setCanResend(true);
          clearInterval(intervalRef.current); // Clear the interval when the timer reaches 0
          return 0;
        }
        return prevTimer - 1;
      });
    }, 1000);

    // Cleanup the interval when the component is unmounted
    return () => clearInterval(intervalRef.current);
  }, [router]);

  const handleSubmit = async (formData) => {
    try {
      const session_user_id = sessionStorage.getItem('user_id');

      if (!session_user_id) {
        setError('Session expired. Please login again');
        sessionStorage.clear();
        router.push(`${BASE_ROUTE}/login`);
        return;
      }

      const userId = await decrypt(session_user_id);
      formData.append('user_id', userId);
    } catch (error) {
      console.error('Error decrypting user_id:', error);
      setError('Something went wrong, could not send OTP. Try again');
      return;
    }
    const result = await verifyOtpAction(formData);
    if (result.error) {
      setError(result.error);
      setSuccessMessage('');
    } else if (result.success) {
      setSuccessMessage(result.success);
      setError('');
      sessionStorage.clear();
      router.push(`${DEFAULT_LOGIN_REDIRECT}`);
    };
  };

  const handleResendOtp = async () => {
    try {
      const session_user_id = sessionStorage.getItem('user_id');

      if (!session_user_id) {
        setError('Session expired. Please login again');
        sessionStorage.clear();
        router.push(`${BASE_ROUTE}/login`);
        return;
      }

      const userId = await decrypt(session_user_id);
      const result = await resendOtpAction(userId);

      if (result.error) {
        setError(result.error);
        setSuccessMessage('');
      };

      if (result.success) {
        setSuccessMessage(result.success);
        setError('');
        sessionStorage.setItem('otpExpiry', Date.now() + 600000);
      };
    } catch (error) {
      console.error('Error decrypting user_id:', error);
      setError('Something went wrong, could not send OTP. Try again');
      return;
    };

    setTimer(60);
    setCanResend(false);

    clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => {
      setTimer((prevTimer) => {
        if (prevTimer === 0) {
          setCanResend(true);
          clearInterval(intervalRef.current); // Clear interval when timer reaches 0
          return 0;
        }
        return prevTimer - 1;
      });
    }, 1000);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>OTP Verification</h1>
      <form className={styles.form} action={handleSubmit}>
        <div className={styles.inputGroup}>
          <label htmlFor="otp">Enter the OTP sent in your mail:</label>
          <input type="text" id="otp" name="otp" required />
        </div>
        <OtpVerifyButton />
        <ResendOtpButton
        onClick={handleResendOtp}
        disabled={!canResend}
        timer={timer}
        />
      </form>
      {error && <p className={styles.error}>{error}</p>}
      {successMessage && <p className={styles.success}>{successMessage}</p>}
    </div>
  );
}