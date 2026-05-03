/**
 * Vitest global test setup.
 *
 * This file is loaded before every test suite via the setupFiles
 * option in vite.config.ts. It extends Vitest matchers with
 * DOM-specific assertions (toBeInTheDocument, toHaveTextContent, etc.).
 */
import "@testing-library/jest-dom";
