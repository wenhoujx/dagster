import {render, screen} from '@testing-library/react';
import * as React from 'react';

import {Button} from './Button';
import {MaybeTooltip} from './MaybeTooltip';

describe('MaybeTooltip', () => {
  it('renders with a tooltip wrapper if `hasTooltip` is true', async () => {
    render(
      <MaybeTooltip hasTooltip tooltipProps={{content: 'Hello world'}}>
        <Button>Lorem</Button>
      </MaybeTooltip>,
    );

    const wrapper = document.getElementsByClassName('bp3-popover2-target');
    expect(wrapper.length).toBe(1);
    const button = screen.queryByRole('button', {name: /lorem/i});
    expect(wrapper[0]!.contains(button));
  });

  it('does not render with a tooltip wrapper if `hasTooltip` is false', async () => {
    render(
      <MaybeTooltip hasTooltip={false} tooltipProps={{content: 'Hello world'}}>
        <Button>Lorem</Button>
      </MaybeTooltip>,
    );

    const wrapper = document.getElementsByClassName('bp3-popover2-target');
    expect(wrapper.length).toBe(0);
    const button = screen.queryByRole('button', {name: /lorem/i});
    expect(button).toBeVisible();
  });
});
