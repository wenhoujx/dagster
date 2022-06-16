import {Meta} from '@storybook/react/types-6-0';
import * as React from 'react';

import {Box} from './Box';
import {Button} from './Button';
import {Checkbox} from './Checkbox';
import {MaybeTooltip} from './MaybeTooltip';

// eslint-disable-next-line import/no-default-export
export default {
  title: 'MaybeTooltip',
  component: MaybeTooltip,
} as Meta;

export const Example = () => {
  const [disabled, setDisabled] = React.useState(true);
  return (
    <Box flex={{direction: 'column', alignItems: 'flex-start', gap: 12}}>
      <Checkbox
        format="switch"
        checked={disabled}
        onChange={() => setDisabled((current) => !current)}
        label="Disable button?"
      />
      <MaybeTooltip tooltipProps={{content: 'I am a disabled button!'}} hasTooltip={disabled}>
        <Button disabled={disabled}>{disabled ? 'Disabled' : 'Enabled'}</Button>
      </MaybeTooltip>
    </Box>
  );
};
