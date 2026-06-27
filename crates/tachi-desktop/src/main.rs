use std::path::PathBuf;

fn parse_args() -> (PathBuf, bool) {
    let mut args = std::env::args().skip(1);
    let mut headless = false;
    let mut repo_root = None;
    while let Some(arg) = args.next() {
        if arg == "--headless" {
            headless = true;
            continue;
        }
        if arg == "--repo-root" {
            if let Some(value) = args.next() {
                repo_root = Some(PathBuf::from(value));
            }
        }
    }

    (
        repo_root.unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))),
        headless,
    )
}

#[cfg(target_os = "macos")]
mod macos_ui {
    use std::ffi::{c_char, c_void, CStr, CString};
    use std::path::PathBuf;
    use std::ptr;

    type Id = *mut c_void;
    type Sel = *mut c_void;

    #[link(name = "AppKit", kind = "framework")]
    extern "C" {}

    #[link(name = "Foundation", kind = "framework")]
    extern "C" {}

    #[link(name = "objc")]
    extern "C" {
        fn objc_getClass(name: *const c_char) -> Id;
        fn sel_registerName(name: *const c_char) -> Sel;
        fn objc_msgSend();
    }

    const NS_APPLICATION_ACTIVATION_POLICY_REGULAR: isize = 0;

    const NS_WINDOW_STYLE_MASK_TITLED: u64 = 1 << 0;
    const NS_WINDOW_STYLE_MASK_CLOSABLE: u64 = 1 << 1;
    const NS_WINDOW_STYLE_MASK_MINIATURIZABLE: u64 = 1 << 2;
    const NS_WINDOW_STYLE_MASK_RESIZABLE: u64 = 1 << 3;

    unsafe fn class(name: &str) -> Id {
        let c_name = CString::new(name).expect("class name");
        objc_getClass(c_name.as_ptr())
    }

    unsafe fn sel(name: &str) -> Sel {
        let c_name = CString::new(name).expect("selector name");
        sel_registerName(c_name.as_ptr())
    }

    unsafe fn send0<R>(receiver: Id, selector: Sel) -> R {
        let f: extern "C" fn(Id, Sel) -> R = std::mem::transmute(objc_msgSend as *const ());
        f(receiver, selector)
    }

    unsafe fn send1<A, R>(receiver: Id, selector: Sel, arg: A) -> R {
        let f: extern "C" fn(Id, Sel, A) -> R = std::mem::transmute(objc_msgSend as *const ());
        f(receiver, selector, arg)
    }

    unsafe fn send4<A, B, C, D, R>(
        receiver: Id,
        selector: Sel,
        arg1: A,
        arg2: B,
        arg3: C,
        arg4: D,
    ) -> R {
        let f: extern "C" fn(Id, Sel, A, B, C, D) -> R =
            std::mem::transmute(objc_msgSend as *const ());
        f(receiver, selector, arg1, arg2, arg3, arg4)
    }

    pub unsafe fn choose_repo_root(default_root: PathBuf) -> PathBuf {
        let panel_class = class("NSOpenPanel");
        let panel: Id = send0(panel_class, sel("openPanel"));
        let _: () = send1(panel, sel("setCanChooseDirectories:"), true);
        let _: () = send1(panel, sel("setCanChooseFiles:"), false);
        let _: () = send1(panel, sel("setAllowsMultipleSelection:"), false);
        let _: () = send1(panel, sel("setCanCreateDirectories:"), true);

        let default_root_string =
            CString::new(default_root.display().to_string()).expect("default repo root");
        let ns_string_class = class("NSString");
        let default_path: Id = send1(
            ns_string_class,
            sel("stringWithUTF8String:"),
            default_root_string.as_ptr(),
        );
        let url_class = class("NSURL");
        let default_url: Id = send1(url_class, sel("fileURLWithPath:"), default_path);
        let _: () = send1(panel, sel("setDirectoryURL:"), default_url);

        let response: i64 = send0(panel, sel("runModal"));
        if response != 1 {
            return default_root;
        }

        let selected_url: Id = send0(panel, sel("URL"));
        let selected_path: Id = send0(selected_url, sel("path"));
        let c_path: *const c_char = send0(selected_path, sel("UTF8String"));
        if c_path.is_null() {
            return default_root;
        }

        let selected = CStr::from_ptr(c_path).to_string_lossy().into_owned();
        PathBuf::from(selected)
    }

    pub unsafe fn launch(repo_root: PathBuf) {
        let app_class = class("NSApplication");
        let app: Id = send0(app_class, sel("sharedApplication"));
        let _: () = send1(
            app,
            sel("setActivationPolicy:"),
            NS_APPLICATION_ACTIVATION_POLICY_REGULAR,
        );

        let pool_class = class("NSAutoreleasePool");
        let pool: Id = send0(pool_class, sel("new"));

        let window_style = NS_WINDOW_STYLE_MASK_TITLED
            | NS_WINDOW_STYLE_MASK_CLOSABLE
            | NS_WINDOW_STYLE_MASK_MINIATURIZABLE
            | NS_WINDOW_STYLE_MASK_RESIZABLE;

        let rect = (0.0_f64, 0.0_f64, 900.0_f64, 700.0_f64);
        let window_class = class("NSWindow");
        let window: Id = send0(window_class, sel("alloc"));
        let window: Id = send4(
            window,
            sel("initWithContentRect:styleMask:backing:defer:"),
            rect,
            window_style,
            2_u64,
            0,
        );

        let title = CString::new("Tachi Desktop").expect("title");
        let title_string: Id = send1(
            class("NSString"),
            sel("stringWithUTF8String:"),
            title.as_ptr(),
        );
        let _: () = send1(window, sel("setTitle:"), title_string);

        let text_view_class = class("NSTextView");
        let text_view: Id = send0(text_view_class, sel("alloc"));
        let text_view: Id = send1(text_view, sel("initWithFrame:"), rect);

        let app_state = tachi_desktop::app::DesktopApp::new(repo_root);
        let rendered = CString::new(app_state.render_text()).expect("rendered text");
        let ns_string_class = class("NSString");
        let text: Id = send1(
            ns_string_class,
            sel("stringWithUTF8String:"),
            rendered.as_ptr(),
        );
        let _: () = send1(text_view, sel("setString:"), text);

        let content_view: Id = send0(window, sel("contentView"));
        let _: () = send1(content_view, sel("addSubview:"), text_view);
        let _: () = send1(
            window,
            sel("makeKeyAndOrderFront:"),
            ptr::null_mut::<c_void>(),
        );
        let _: () = send1(app, sel("activateIgnoringOtherApps:"), 1_isize);
        let _: () = send0(app, sel("run"));
        let _: Id = send0(pool, sel("drain"));
    }
}

fn main() {
    let (repo_root, headless) = parse_args();
    if headless {
        let app = tachi_desktop::app::DesktopApp::new(repo_root);
        println!("{}", app.render_text());
        return;
    }
    #[cfg(target_os = "macos")]
    unsafe {
        let repo_root = macos_ui::choose_repo_root(repo_root);
        macos_ui::launch(repo_root);
    }

    #[cfg(not(target_os = "macos"))]
    {
        let app = tachi_desktop::app::DesktopApp::new(repo_root);
        println!("{}", app.render_text());
    }
}
