import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GeometricRenderer } from './GeometricRenderer';

describe('GeometricRenderer', () => {
  it('renders svg geometric path', () => {
    render(<GeometricRenderer data-testid="geo" />);
    expect(screen.getByTestId('geo').tagName.toLowerCase()).toBe('svg');
  });

  it('renders optional edge line segments', () => {
    render(
      <GeometricRenderer
        data-testid="geo"
        points={[
          { x: 10, y: 20 },
          { x: 90, y: 80 },
        ]}
        edges={[
          {
            source: { x: 10, y: 20 },
            target: { x: 90, y: 80 },
          },
        ]}
      />,
    );

    expect(screen.getAllByTestId('geometric-renderer-edge')).toHaveLength(1);
  });
});
