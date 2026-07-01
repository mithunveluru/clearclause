import type { Variants } from "framer-motion";

export const easeSmooth = [0.22, 1, 0.36, 1] as const;

export const fadeUp: Variants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.55, ease: easeSmooth } },
};

export const staggerContainer: Variants = {
  animate: { transition: { staggerChildren: 0.06, delayChildren: 0.05 } },
};

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.5, ease: easeSmooth } },
};

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.975 },
  animate: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: easeSmooth } },
};
