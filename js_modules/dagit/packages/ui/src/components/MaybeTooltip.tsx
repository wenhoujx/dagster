import * as React from 'react';

import {Tooltip} from './Tooltip';

interface Props {
  hasTooltip: boolean;
  tooltipProps: React.ComponentProps<typeof Tooltip>;
}

export const MaybeTooltip: React.FC<Props> = ({children, hasTooltip, tooltipProps}) =>
  hasTooltip ? <Tooltip {...tooltipProps}>{children}</Tooltip> : <>{children}</>;
