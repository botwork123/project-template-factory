import { describe, expect, it } from 'vitest';
import { add } from '../src/index';

describe('smoke', () => {
  it('adds', () => {
    expect(add(1, 1)).toBe(2);
  });
});
