package dk.bearware.gui;

import dk.bearware.UserRight;

/**
 * Xray admin helper: constants and utilities used by the ported
 * TeamTalk Plus administration screens.
 */
public class XrayAdmin {

    /** Default rights for a freshly created (non-admin) user account. */
    public static final int DEFAULT_USER_RIGHTS =
            UserRight.USERRIGHT_MULTI_LOGIN
            | UserRight.USERRIGHT_VIEW_ALL_USERS
            | UserRight.USERRIGHT_CREATE_TEMPORARY_CHANNEL
            | UserRight.USERRIGHT_MODIFY_CHANNELS
            | UserRight.USERRIGHT_TEXTMESSAGE_BROADCAST
            | UserRight.USERRIGHT_KICK_USERS
            | UserRight.USERRIGHT_BAN_USERS
            | UserRight.USERRIGHT_MOVE_USERS
            | UserRight.USERRIGHT_OPERATOR_ENABLE
            | UserRight.USERRIGHT_UPLOAD_FILES
            | UserRight.USERRIGHT_DOWNLOAD_FILES
            | UserRight.USERRIGHT_UPDATE_SERVERPROPERTIES
            | UserRight.USERRIGHT_TRANSMIT_VOICE
            | UserRight.USERRIGHT_TRANSMIT_VIDEOCAPTURE
            | UserRight.USERRIGHT_TRANSMIT_DESKTOP
            | UserRight.USERRIGHT_TRANSMIT_DESKTOPINPUT
            | UserRight.USERRIGHT_TRANSMIT_MEDIAFILE_AUDIO
            | UserRight.USERRIGHT_TRANSMIT_MEDIAFILE_VIDEO
            | UserRight.USERRIGHT_TEXTMESSAGE_USER
            | UserRight.USERRIGHT_TEXTMESSAGE_CHANNEL
            | UserRight.USERRIGHT_RECORD_VOICE
            | UserRight.USERRIGHT_VIEW_HIDDEN_CHANNELS;

    /** Rights that are only given to server administrators. */
    public static final int ADMIN_ONLY_RIGHTS =
            UserRight.USERRIGHT_UPDATE_SERVERPROPERTIES
            | UserRight.USERRIGHT_BAN_USERS
            | UserRight.USERRIGHT_KICK_USERS
            | UserRight.USERRIGHT_MOVE_USERS
            | UserRight.USERRIGHT_CREATE_TEMPORARY_CHANNEL
            | UserRight.USERRIGHT_MODIFY_CHANNELS
            | UserRight.USERRIGHT_VIEW_HIDDEN_CHANNELS;

    private XrayAdmin() {}
}
