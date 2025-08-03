export interface ColorTokens {
  // 品牌主色调
  primary: {
    900: string; // #000000 - 纯黑
    800: string; // #081727 - 深蓝黑
    700: string; // #161b25 - 深蓝灰
    500: string; // #2b3a4f - 中蓝灰
    300: string; // #c9d4dc - 浅蓝灰
    100: string; // #ffffff - 纯白
  };
  
  // 品牌强调色
  accent: {
    500: string; // #2b3a4f - 品牌强调色
    400: string; // #3d4e63 - 中等强调
    300: string; // #5a6b7d - 浅强调
    200: string; // #8a9ba8 - 极浅强调
    100: string; // #e8eef2 - 背景高亮
  };
  
  // 功能色彩
  semantic: {
    success: {
      500: string; // #28a745
      100: string; // #d4edda
    };
    warning: {
      500: string; // #ffc107
      100: string; // #fff3cd
    };
    error: {
      500: string; // #dc3545
      100: string; // #f8d7da
    };
    info: {
      500: string; // #17a2b8
      100: string; // #d1ecf1
    };
  };
  
  // 中性色彩
  neutral: {
    white: string;   // #ffffff
    gray: {
      50: string;    // #fafafa
      100: string;   // #f5f5f5
      200: string;   // #eeeeee
      300: string;   // #e0e0e0
      400: string;   // #bdbdbd
      500: string;   // #9e9e9e
      600: string;   // #757575
      700: string;   // #616161
      800: string;   // #424242
      900: string;   // #212121
    };
    black: string;   // #000000
  };
}

export const colorTokens: ColorTokens = {
  primary: {
    900: '#000000',
    800: '#081727',
    700: '#161b25',
    500: '#2b3a4f',
    300: '#c9d4dc',
    100: '#ffffff',
  },
  accent: {
    500: '#2b3a4f',
    400: '#3d4e63',
    300: '#5a6b7d',
    200: '#8a9ba8',
    100: '#e8eef2',
  },
  semantic: {
    success: {
      500: '#28a745',
      100: '#d4edda',
    },
    warning: {
      500: '#ffc107',
      100: '#fff3cd',
    },
    error: {
      500: '#dc3545',
      100: '#f8d7da',
    },
    info: {
      500: '#17a2b8',
      100: '#d1ecf1',
    },
  },
  neutral: {
    white: '#ffffff',
    gray: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: '#9e9e9e',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    },
    black: '#000000',
  },
};