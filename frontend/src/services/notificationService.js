import { toast } from 'react-toastify';

const rootStyles = getComputedStyle(document.documentElement);

const toastSuccessBg = rootStyles.getPropertyValue('--toast-success-bg').trim();
const toastErrorBg = rootStyles.getPropertyValue('--toast-error-bg').trim();
const toastInfoBg = rootStyles.getPropertyValue('--toast-info-bg').trim();
const toastWarningBg = rootStyles.getPropertyValue('--toast-warning-bg').trim();
const toastTextColor = rootStyles.getPropertyValue('--toast-text-color').trim();

export const notifySuccess = (message) =>
  toast.success(message, {
    style: { backgroundColor: toastSuccessBg, color: toastTextColor },
  });

export const notifyError = (message) =>
  toast.error(message, {
    style: { backgroundColor: toastErrorBg, color: toastTextColor },
  });

export const notifyInfo = (message) =>
  toast.info(message, {
    style: { backgroundColor: toastInfoBg, color: toastTextColor },
  });

export const notifyWarning = (message) =>
  toast.warning(message, {
    style: { backgroundColor: toastWarningBg, color: toastTextColor },
  });