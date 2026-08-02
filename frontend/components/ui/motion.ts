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

/** Props for a view swapped inside the explorer's `<AnimatePresence mode="wait">`.
 *
 * `mode="wait"` holds the incoming view until the outgoing one has finished exiting — with
 * no `exit` that resolves immediately, so the crossfade these views were written for never
 * actually played. Spread this rather than restating the three props per view. */
export const viewTransition = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
  transition: { duration: 0.22, ease: easeSmooth },
} as const;

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.975 },
  animate: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: easeSmooth } },
};
